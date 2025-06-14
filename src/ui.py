from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from src.options import Option
from src.scene import Scene
import pyglet

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

class DaySummaryView(UIComponent):
    """Display end of day results"""
    
    def __init__(self, day_results, window_width, window_height):
        self.day_results = day_results
        self.window_width = window_width
        self.window_height = window_height
        self.batch = pyglet.graphics.Batch()
        
        # Title
        self.title = pyglet.text.Label(
            "Day Complete!",
            x=window_width // 2,
            y=window_height - 100,
            anchor_x='center',
            font_size=24,
            batch=self.batch
        )
        
        # Results text
        results_text = self._format_results()
        self.results_label = pyglet.text.Label(
            results_text,
            x=window_width // 2,
            y=window_height // 2,
            width=window_width * 0.8,
            multiline=True,
            anchor_x='center',
            anchor_y='center',
            batch=self.batch
        )
        
        # Buttons
        self.save_button = pyglet.shapes.Rectangle(
            window_width * 0.2, 100, 200, 50,
            color=(100, 100, 200),
            batch=self.batch
        )
        self.save_label = pyglet.text.Label(
            "Save Game",
            x=window_width * 0.2 + 100,
            y=125,
            anchor_x='center',
            anchor_y='center',
            batch=self.batch
        )
        
        self.continue_button = pyglet.shapes.Rectangle(
            window_width * 0.6, 100, 200, 50,
            color=(100, 200, 100),
            batch=self.batch
        )
        self.continue_label = pyglet.text.Label(
            "Next Day",
            x=window_width * 0.6 + 100,
            y=125,
            anchor_x='center',
            anchor_y='center',
            batch=self.batch
        )
    
    def _format_results(self):
        """Format day results for display"""
        text = "Today's Results:\n\n"
        total_score = 0
        
        for i, scene_result in enumerate(self.day_results):
            text += f"Scene {i+1}:\n"
            text += f"  Options selected: {', '.join(scene_result.get('selected_options', []))}\n"
            
            effects = scene_result.get('effects', {})
            if effects:
                text += "  Effects:\n"
                for name, value in effects.items():
                    text += f"    {name}: {value:+.1f}\n"
            
            score = scene_result.get('score', 0)
            text += f"  Score: {score:.1f}\n\n"
            total_score += score
        
        text += f"Total Score: {total_score:.1f}"
        return text
    
    def draw(self):
        self.batch.draw()
    
    def update(self, dt):
        pass
    
    def on_mouse_press(self, x, y):
        # Check save button
        if (self.save_button.x <= x <= self.save_button.x + 200 and
            self.save_button.y <= y <= self.save_button.y + 50):
            return 'save'
        
        # Check continue button
        if (self.continue_button.x <= x <= self.continue_button.x + 200 and
            self.continue_button.y <= y <= self.continue_button.y + 50):
            return 'continue'
        
        return None

class GameCompleteView(UIComponent):
    """Display game completion screen"""
    
    def __init__(self, window_width, window_height):
        self.batch = pyglet.graphics.Batch()
        
        self.label = pyglet.text.Label(
            "Game Complete!\nThanks for playing!",
            x=window_width // 2,
            y=window_height // 2,
            anchor_x='center',
            anchor_y='center',
            font_size=32,
            multiline=True,
            align='center',
            batch=self.batch
        )
    
    def draw(self):
        self.batch.draw()
    
    def update(self, dt):
        pass
