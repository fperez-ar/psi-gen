# game_architecture.py
from dataclasses import dataclass, field
from typing import List, Dict, Any
import pyglet
import yaml
from pathlib import Path

from src.data_loader import DataLoader
from src.effect import Effect
from src.scene import Scene
from src.day import Day
from src.ui import SceneView

@dataclass
class GameState:
    """Overall game state"""
    current_day_index: int = 0
    current_scene_index: int = 0
    days: List[Day] = field(default_factory=list)
    global_stats: Dict[str, float] = field(default_factory=dict)
    day_results: List[Dict[str, Any]] = field(default_factory=list)

# ========== Game Logic ==========

class EffectCalculator:
    """Calculates effects and scores"""
    
    @staticmethod
    def calculate_scene_effects(scene: Scene) -> Dict[str, float]:
        """Calculate total effects from selected options"""
        effects = {}
        
        for option in scene.options:
            if option.selected:
                for effect in option.effects:
                    if effect.name not in effects:
                        effects[effect.name] = 0
                    effects[effect.name] += effect.value
        
        return effects
    
    @staticmethod
    def compare_with_expected(calculated: Dict[str, float], expected: List[Effect]) -> float:
        """Compare calculated effects with expected outcome"""
        score = 0.0
        
        for exp_effect in expected:
            if exp_effect.name in calculated:
                # Simple scoring: closer to expected = higher score
                diff = abs(calculated[exp_effect.name] - exp_effect.value)
                score += max(0, 100 - diff * 10)  # Mock scoring
        
        return score

class GameSaveManager:
    """Handles saving and loading game state"""
    
    @staticmethod
    def save_game(state: GameState, filepath: str):
        """Save game state to YAML"""
        save_data = {
            'current_day': state.current_day_index,
            'current_scene': state.current_scene_index,
            'global_stats': state.global_stats,
            'day_results': state.day_results
        }
        
        with open(filepath, 'w') as f:
            yaml.dump(save_data, f)
    
    @staticmethod
    def load_game(filepath: str) -> Dict[str, Any]:
        """Load game state from YAML"""
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)

# ========== Main Game Class ==========

class DaySceneGame:
    """Main game controller"""
    
    def __init__(self, window: pyglet.window.Window, data_dir: str):
        self.window = window
        self.data_loader = DataLoader(Path(data_dir))
        
        # Load game data
        self.data_loader.load_effects()
        self.data_loader.load_options()
        
        # Initialize game state
        self.state = GameState()
        self.state.days = self.data_loader.load_days()
        
        # Current view
        self.current_view = None
        self.calculator = EffectCalculator()
        self.save_manager = GameSaveManager()
        
        # Start first scene
        self.load_current_scene()
    
    def load_current_scene(self):
        """Load the current scene view"""
        day = self.state.days[self.state.current_day_index]
        scene = day.scenes[self.state.current_scene_index]
        
        self.current_view = SceneView(scene, self.window.width, self.window.height)
    
    def on_submit(self):
        """Handle scene submission"""
        scene = self.get_current_scene()
        
        # Calculate effects
        effects = self.calculator.calculate_scene_effects(scene)
        scene.calculated_effects = effects
        
        # Calculate score
        score = self.calculator.compare_with_expected(effects, scene.outcome.expected)
        
        # Store results
        scene_result = {
            'scene_index': self.state.current_scene_index,
            'selected_options': [opt.name for opt in scene.options if opt.selected],
            'effects': effects,
            'score': score
        }
        
        # Move to next scene or end of day
        self.state.current_scene_index += 1
        
        if self.state.current_scene_index >= len(self.get_current_day().scenes):
            self.show_day_summary()
        else:
            self.load_current_scene()
    
    def show_day_summary(self):
        """Display end of day summary"""
        # Create summary view with results
        pass
    
    def next_day(self):
        """Move to next day"""
        self.state.current_day_index += 1
        self.state.current_scene_index = 0
        self.state.day_results.append({})  # Store day results
        
        if self.state.current_day_index < len(self.state.days):
            self.load_current_scene()
        else:
            self.show_game_complete()
    
    def save_game(self):
        """Save current game state"""
        self.save_manager.save_game(self.state, "save.yaml")
    
    def get_current_day(self) -> Day:
        return self.state.days[self.state.current_day_index]
    
    def get_current_scene(self) -> Scene:
        return self.get_current_day().scenes[self.state.current_scene_index]
