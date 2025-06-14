from dataclasses import dataclass, field
from typing import List, Dict
from src.effect import Effect, EffectDefinition
from src.scene import Scene, SceneOutcome
from src.options import Option
from src.day import Day
from pathlib import Path
import yaml

class DataLoader:
    """Handles loading game data from YAML files"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.effects_cache: Dict[str, EffectDefinition] = {}
        self.options_cache: Dict[str, Option] = {}
        
    def load_effects(self) -> Dict[str, EffectDefinition]:
        """Load all effect definitions"""
        with open(self.data_dir / "effects.yaml", 'r') as f:
            data = yaml.safe_load(f)
        
        for effect_data in data:
            effect_def = EffectDefinition(
                name=effect_data['name'],
                text=effect_data['text'],
                effects=[Effect(**e) for e in effect_data.get('effects', [])]
            )
            self.effects_cache[effect_def.name] = effect_def
        
        return self.effects_cache
    
    def load_options(self) -> Dict[str, Option]:
        """Load all option definitions"""
        with open(self.data_dir / "options.yaml", 'r') as f:
            data = yaml.safe_load(f)
        
        for option_data in data:
            option = Option(
                name=option_data['name'],
                text=option_data['text'],
                effects=[Effect(**e) for e in option_data.get('effects', [])]
            )
            self.options_cache[option.name] = option
        
        return self.options_cache
    
    def load_scene(self, scene_file: str) -> Scene:
        """Load a single scene from YAML"""
        with open(self.data_dir / scene_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Create options from references
        options = []
        for opt_name in data['options']:
            if opt_name in self.options_cache:
                # Create a copy to avoid shared state
                opt = self.options_cache[opt_name]
                options.append(Option(
                    name=opt.name,
                    text=opt.text,
                    effects=opt.effects.copy()
                ))
        
        outcome = SceneOutcome(
            expected=[Effect(**e) for e in data['outcome']['expected']]
        )
        
        return Scene(
            bg_images=data['bg_images'],
            fg_text=data['fg_text'],
            stats=data.get('stats', {}),
            options=options,
            button_text=data['button_text'],
            outcome=outcome
        )
    
    def load_days(self) -> List[Day]:
        """Load all days and their scenes"""
        with open(self.data_dir / "days.yaml", 'r') as f:
            days_data = yaml.safe_load(f)
        
        days = []
        for day_data in days_data:
            scenes = []
            for scene_file in day_data['scenes']:
                scenes.append(self.load_scene(scene_file))
            
            days.append(Day(
                text=day_data['text'],
                scenes=scenes
            ))
        
        return days
