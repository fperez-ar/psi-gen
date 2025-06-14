from dataclasses import dataclass, field
from typing import List
from src.effect import Effect

@dataclass
class Option:
    """Represents a choice the player can make"""
    name: str
    text: str
    effects: List[Effect] = field(default_factory=list)
    selected: bool = False