#!/usr/bin/env python3
"""Generate Telegram alerts when the Mission Control Kanban changes."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from kanban_utils import BoardState, Card, load_board, summarize_delta

STATE_CACHE = Path("kanban-board/.cache/kanban_state.json")
STATE_CACHE.parent.mkdir(parents=True, exist_ok=True)
COLUMN_EMOJI = {
    "Backlog": "📝",
    "In Progress": "⚒️",
    "Review / Verification": "🕵️",
    "Done": "✅",
}
TELEGRAM_TO = "telegram:6308720344"


def load_prev_state() -> BoardState | None:
    if not STATE_CACHE.exists():
        return None
    data = json.loads(STATE_CACHE.read_text())
    return BoardState.from_dict(data)


def save_state(state: BoardState) -> None:
    STATE_CACHE.write_text(json.dumps(state.to_dict(), indent=2))


def describe_change(card: Card, change: str, column: str) -> str:
    if change == "added":
        verb = f"moved into {column}"
    elif change == "removed":
        verb = f"left {column}"
    elif change == "status":
        verb = "marked done" if card.done else "reopened"
    else:
        verb = "updated"
    return f"{card.title} — {verb} (owner: {card.owner})"


def build_message(delta: Dict[str, List[Tuple[Card, str]]], board_updated: str) -> str:
    timestamp = datetime.now().strftime("%H:%M MST")
    lines = [f"Jobs alert — {timestamp}"]
    for column in ["Done", "In Progress", "Review / Verification", "Backlog"]:
        entries = delta.get(column)
        if not entries:
            continue
        emoji = COLUMN_EMOJI.get(column, "•")
        for card, change in entries:
            lines.append(f"{emoji} {describe_change(card, change, column)}")
    lines.append(f"Board updated: {board_updated or 'n/a'}")
    return "\n".join(lines)


def send_telegram(message: str, dry_run: bool = False) -> None:
    if dry_run:
        print("[dry-run] Telegram message:\n" + message)
        return
    subprocess.run(
        [
            "openclaw",
            "message",
            "send",
            "--channel",
            "telegram",
            "--to",
            TELEGRAM_TO,
            "--message",
            message,
        ],
        check=True,
    )


def run(dry_run: bool = False) -> None:
    current = load_board()
    previous = load_prev_state()
    if previous is None:
        save_state(current)
        print("Initialized state cache; no alerts sent.")
        return

    delta = summarize_delta(previous, current)
    if not delta:
        print("No board changes detected.")
        return

    message = build_message(delta, current.updated)
    send_telegram(message, dry_run=dry_run)
    save_state(current)
    print("Alert dispatched.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print message without sending")
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()

