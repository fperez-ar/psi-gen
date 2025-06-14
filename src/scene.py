from dataclasses import dataclass, field
from typing import List, Dict
from src.effect import Effect
from src.options import Option

@dataclass
class SceneOutcome:
    """Expected outcome for a scene"""
    expected: List[Effect] = field(default_factory=list)

@dataclass
class Scene:
    """Represents a single scene within a day"""
    bg_images: List[str]
    fg_text: str
    stats: Dict[str, float]
    options: List[Option]
    button_text: str
    outcome: SceneOutcome
    
    # Runtime data
    selected_options: List[Option] = field(default_factory=list)
    calculated_effects: Dict[str, float] = field(default_factory=dict)
