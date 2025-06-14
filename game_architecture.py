# game_architecture.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
import pyglet
import yaml
from pathlib import Path

# ========== Data Models ==========

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

@dataclass
class Option:
    """Represents a choice the player can make"""
    name: str
    text: str
    effects: List[Effect] = field(default_factory=list)
    selected: bool = False

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

@dataclass
class Day:
    """Represents a game day"""
    text: str
    scenes: List[Scene]

@dataclass
class GameState:
    """Overall game state"""
    current_day_index: int = 0
    current_scene_index: int = 0
    days: List[Day] = field(default_factory=list)
    global_stats: Dict[str, float] = field(default_factory=dict)
    day_results: List[Dict[str, Any]] = field(default_factory=list)

# ========== Data Loading ==========

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

# ========== UI Components ==========

class UIComponent(ABC):
    """Base class for UI components"""
    
    @abstractmethod
    def draw(self):
        pass
    
    @abstractmethod
    def update(self, dt):
        pass

class OptionButton(UIComponent):
    """Clickable option with tooltip"""
    
    def __init__(self, option: Option, x: int, y: int, width: int, height: int, batch: pyglet.graphics.Batch):
        self.option = option
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.batch = batch
        self.hovered = False
        
        # Create visual elements
        self.background = pyglet.shapes.Rectangle(
            x, y, width, height,
            color=(100, 100, 100) if not option.selected else (150, 200, 150),
            batch=batch
        )
        
        self.label = pyglet.text.Label(
            option.text,
            x=x + width//2,
            y=y + height//2,
            anchor_x='center',
            anchor_y='center',
            batch=batch
        )
        
        self.tooltip = None
        
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is within button bounds"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def on_mouse_motion(self, x: int, y: int):
        """Handle mouse hover"""
        was_hovered = self.hovered
        self.hovered = self.contains_point(x, y)
        
        if self.hovered and not was_hovered:
            # Show tooltip
            self._create_tooltip(x, y)
        elif not self.hovered and was_hovered:
            # Hide tooltip
            self._destroy_tooltip()
    
    def on_mouse_press(self, x: int, y: int):
        """Handle click"""
        if self.contains_point(x, y):
            self.option.selected = not self.option.selected
            self.background.color = (150, 200, 150) if self.option.selected else (100, 100, 100)
            return True
        return False
    
    def _create_tooltip(self, x: int, y: int):
        """Create tooltip showing effect information"""
        # Implementation for tooltip display
        pass
    
    def _destroy_tooltip(self):
        """Remove tooltip"""
        if self.tooltip:
            self.tooltip = None
    
    def draw(self):
        # Drawing is handled by batch
        pass
    
    def update(self, dt):
        pass

class SceneView(UIComponent):
    """Displays a single scene"""
    
    def __init__(self, scene: Scene, window_width: int, window_height: int):
        self.scene = scene
        self.window_width = window_width
        self.window_height = window_height
        
        self.batch = pyglet.graphics.Batch()
        self.bg_sprites = []
        self.option_buttons = []
        
        self._setup_background()
        self._setup_text()
        self._setup_options()
        self._setup_submit_button()
        
    def _setup_background(self):
        """Load and setup background images"""
        # for img_path in self.scene.bg_images:
        #     image = pyglet.image.load(img_path)
        #     sprite = pyglet.sprite.Sprite(image, batch=self.batch)
        #     self.bg_sprites.append(sprite)
    
    def _setup_text(self):
        """Setup foreground text"""
        self.fg_label = pyglet.text.Label(
            self.scene.fg_text,
            x=self.window_width // 2,
            y=self.window_height * 0.7,
            width=self.window_width * 0.8,
            multiline=True,
            anchor_x='center',
            anchor_y='center',
            batch=self.batch
        )
    
    def _setup_options(self):
        """Create option buttons"""
        start_y = self.window_height * 0.4
        option_height = 50
        option_spacing = 10
        
        for i, option in enumerate(self.scene.options):
            y = start_y - i * (option_height + option_spacing)
            button = OptionButton(
                option,
                x=self.window_width * 0.2,
                y=y,
                width=self.window_width * 0.6,
                height=option_height,
                batch=self.batch
            )
            self.option_buttons.append(button)
    
    def _setup_submit_button(self):
        """Create submit button"""
        self.submit_button = pyglet.shapes.Rectangle(
            self.window_width * 0.4,
            50,
            self.window_width * 0.2,
            40,
            color=(50, 150, 50),
            batch=self.batch
        )
        
        self.submit_label = pyglet.text.Label(
            self.scene.button_text,
            x=self.window_width * 0.5,
            y=70,
            anchor_x='center',
            anchor_y='center',
            batch=self.batch
        )
    
    def draw(self):
        self.batch.draw()
    
    def update(self, dt):
        pass
    
    def on_mouse_motion(self, x, y):
        for button in self.option_buttons:
            button.on_mouse_motion(x, y)
    
    def on_mouse_press(self, x, y):
        # Check option buttons
        for button in self.option_buttons:
            if button.on_mouse_press(x, y):
                return
        
        # Check submit button
        if (self.submit_button.x <= x <= self.submit_button.x + self.submit_button.width and
            self.submit_button.y <= y <= self.submit_button.y + self.submit_button.height):
            return 'submit'

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
