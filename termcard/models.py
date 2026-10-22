from dataclasses import dataclass, field, asdict
from datetime import datetime, date
import uuid


@dataclass
class Card:
    id: str
    front: str
    back: str
    ease_factor: float = 2.5
    interval: int = 0
    repetitions: int = 0
    due: str = field(default_factory=lambda: date.today().isoformat())
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_reviewed: str | None = None
    total_reviews: int = 0

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    @classmethod
    def new(cls, front, back):
        return cls(id=uuid.uuid4().hex[:8], front=front, back=back)

    def is_due(self):
        return date.fromisoformat(self.due) <= date.today()

    def is_new(self):
        return self.total_reviews == 0


@dataclass
class Deck:
    id: str
    name: str
    description: str = ""
    cards: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "cards": [c.to_dict() for c in self.cards],
        }

    @classmethod
    def from_dict(cls, d):
        cards = [Card.from_dict(c) for c in d.get("cards", [])]
        return cls(
            id=d["id"],
            name=d["name"],
            description=d.get("description", ""),
            cards=cards,
            created_at=d.get("created_at", datetime.now().isoformat()),
        )

    @classmethod
    def new(cls, name, description=""):
        return cls(id=uuid.uuid4().hex[:8], name=name, description=description)

    def due_cards(self):
        return [c for c in self.cards if c.is_due()]
