from dataclasses import dataclass
from typing import List
from src.effect import Effect
from src.scene import Scene

@dataclass
class Day:
    """Represents a game day"""
    text: str
    scenes: List[Scene]
