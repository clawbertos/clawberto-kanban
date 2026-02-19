#!/usr/bin/env python3
"""Regenerate kanban-board/index.html from KANBAN.md."""
from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
import re
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).parent
KANBAN_PATH = BASE_DIR / "KANBAN.md"
OUTPUT_PATH = BASE_DIR / "index.html"
TIMEZONE = ZoneInfo("America/Phoenix")
COLUMN_ORDER = [
    "Backlog",
    "In Progress",
    "Review / Verification",
    "Done",
]

CARD_PATTERN = re.compile(
    r"^- \[(?P<state>[ x])\]\s+\*\*(?P<title>.+?)\*\* — (?P<desc>.+?)\. _Owner: (?P<owner>.+?)_",
    re.IGNORECASE,
)
URL_PATTERN = re.compile(r"&lt;(https?://[^&]+)&gt;")


def load_cards() -> dict[str, list[dict[str, str]]]:
    columns: dict[str, list[dict[str, str]]] = {col: [] for col in COLUMN_ORDER}
    current = None
    for raw_line in KANBAN_PATH.read_text().splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current = line[3:].strip()
            continue
        if not line or not current:
            continue
        match = CARD_PATTERN.match(line)
        if not match:
            continue
        data = match.groupdict()
        columns.setdefault(current, []).append(
            {
                "done": data["state"].lower() == "x",
                "title": data["title"].strip(),
                "desc": data["desc"].strip(),
                "owner": data["owner"].strip(),
            }
        )
    return columns


def linkify(text: str) -> str:
    escaped = escape(text)
    return URL_PATTERN.sub(r'<a href="\1">\1</a>', escaped)


def render_card(card: dict[str, str]) -> str:
    classes = "card done" if card["done"] else "card"
    title = escape(card["title"])
    desc = linkify(card["desc"])
    owner = escape(card["owner"])
    return f"""
      <div class=\"{classes}\">
        <div class=\"title\"><strong>{title}</strong></div>
        <div>{desc}.</div>
        <div class=\"owner\">Owner: {owner}</div>
      </div>
    """


def main() -> None:
    columns = load_cards()
    timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M %Z")
    column_html = []
    for column in COLUMN_ORDER:
        cards = columns.get(column, [])
        if not cards and column == "In Progress":
            cards_html = (
                """
      <div class=\"card\">
        <div>Lane is open—pull the next priority from Backlog and drop it here.</div>
      </div>
                """
            )
        else:
            cards_html = "\n".join(render_card(card) for card in cards)
        column_html.append(
            f"""
    <div class=\"column\">
      <h2>{escape(column)}</h2>
{cards_html}
    </div>
            """
        )

    template = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <title>Clawberto Mission Control</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <style>
    body {{
      font-family: \"SF Pro\", \"Inter\", -apple-system, BlinkMacSystemFont, sans-serif;
      background: #0f1115;
      color: #f5f7ff;
      margin: 0;
      padding: 40px;
    }}
    h1 {{
      font-weight: 700;
      letter-spacing: 0.04em;
    }}
    .board {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 20px;
      margin-top: 30px;
    }}
    .column {{
      background: #181c24;
      border-radius: 14px;
      padding: 18px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    }}
    .column h2 {{
      margin-top: 0;
      font-size: 1rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #8fe0ff;
    }}
    .card {{
      background: #0f1219;
      border-radius: 12px;
      padding: 14px;
      margin-bottom: 12px;
      border: 1px solid rgba(255,255,255,0.06);
    }}
    .card.done {{
      border-color: rgba(111, 209, 111, 0.45);
    }}
    .owner {{
      font-size: 0.8rem;
      color: #b5f5d9;
      margin-top: 6px;
    }}
    footer {{
      margin-top: 40px;
      font-size: 0.85rem;
      color: rgba(255,255,255,0.6);
    }}
    a {{ color: #82cfff; }}
  </style>
</head>
<body>
  <h1>Clawberto Mission Control</h1>
  <p>Single source of truth for tasks, agents, and status. Jobs (our Steve Jobs-inspired PM) owns this board and will DM Satya on Telegram for significant changes.</p>
  <p><strong>Last updated:</strong> {timestamp}</p>

  <div class=\"board\">
{''.join(column_html)}
  </div>

  <footer>
    <p>Repo: <a href=\"https://github.com/clawbertos/clawberto-kanban\">github.com/clawbertos/clawberto-kanban</a></p>
    <p>Telegram notifications: triggered by Jobs for significant board changes.</p>
  </footer>
</body>
</html>
"""
    OUTPUT_PATH.write_text("\n".join(line.rstrip() for line in template.splitlines()) + "\n")


if __name__ == "__main__":
    main()
