"""Shared helpers for parsing Mission Control Kanban Markdown."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import re
from typing import Dict, List, Tuple

KANBAN_PATH = Path(__file__).with_name("KANBAN.md")
COLUMN_HEADER_RE = re.compile(r"^##\s+(?P<name>.+)$")
CARD_RE = re.compile(
    r"^- \[(?P<state>[ x])\]\s+\*\*(?P<title>.+?)\*\* — (?P<desc>.+?)\. _Owner: (?P<owner>.+?)_",
    re.IGNORECASE,
)


@dataclass
class Card:
    column: str
    title: str
    description: str
    owner: str
    done: bool

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        return cls(**data)


@dataclass
class BoardState:
    updated: str
    cards: List[Card]

    def to_dict(self) -> dict:
        return {
            "updated": self.updated,
            "cards": [card.to_dict() for card in self.cards],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BoardState":
        cards = [Card.from_dict(entry) for entry in data.get("cards", [])]
        return cls(updated=data.get("updated", ""), cards=cards)


def parse_board(markdown: str) -> BoardState:
    current_column = None
    cards: List[Card] = []
    updated = ""

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line.startswith("_Last updated:"):
            updated = line.strip("_").split(":", 1)[-1].strip()
            continue
        header_match = COLUMN_HEADER_RE.match(line)
        if header_match:
            current_column = header_match.group("name").strip()
            continue
        if not current_column:
            continue
        match = CARD_RE.match(line)
        if not match:
            continue
        data = match.groupdict()
        cards.append(
            Card(
                column=current_column,
                title=data["title"].strip(),
                description=data["desc"].strip(),
                owner=data["owner"].strip(),
                done=data["state"].lower() == "x",
            )
        )
    return BoardState(updated=updated, cards=cards)


def load_board(path: Path | None = None) -> BoardState:
    path = path or KANBAN_PATH
    return parse_board(path.read_text())


def summarize_delta(prev: BoardState, curr: BoardState) -> Dict[str, List[Tuple[Card, str]]]:
    """Compare two board states and return dict of column -> list[(card, change_type)]."""
    by_key_prev = {(card.column, card.title): card for card in prev.cards}
    by_key_curr = {(card.column, card.title): card for card in curr.cards}
    changes: Dict[str, List[Tuple[Card, str]]] = {}

    for key, card in by_key_curr.items():
        prev_card = by_key_prev.get(key)
        if not prev_card:
            change = "added"
        elif prev_card.done != card.done:
            change = "status"
        else:
            change = None
        if change:
            changes.setdefault(card.column, []).append((card, change))

    for key, card in by_key_prev.items():
        if key not in by_key_curr:
            changes.setdefault(card.column, []).append((card, "removed"))

    return changes
