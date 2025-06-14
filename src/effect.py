from typing import List
from dataclasses import dataclass, field

@dataclass
class Effect:
    """Represents a stat modification"""
    name: str
    value: float

    
@dataclass
class EffectDefinition:
    """Definition of an effect with potential sub-effects"""
    name: str
    text: str
    effects: List[Effect] = field(default_factory=list)
