# main.py
import pyglet
from pyglet.window import key
from game_architecture import (
    DaySceneGame, SceneView, UIComponent, 
    EffectCalculator, GameSaveManager, DataLoader
)
from pathlib import Path
import yaml

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

class MainGame(DaySceneGame):
    """Extended game class with full functionality"""
    
    def __init__(self, window, data_dir):
        super().__init__(window, data_dir)
        self.current_day_results = []
        
        # Set up event handlers
        @window.event
        def on_draw():
            window.clear()
            if self.current_view:
                self.current_view.draw()
            
            # Draw day text if in scene view
            if isinstance(self.current_view, SceneView):
                day_text = self.get_current_day().text
                label = pyglet.text.Label(
                    day_text,
                    x=10,
                    y=window.height - 30,
                    font_size=16
                )
                label.draw()
        
        @window.event
        def on_mouse_motion(x, y, dx, dy):
            if hasattr(self.current_view, 'on_mouse_motion'):
                self.current_view.on_mouse_motion(x, y)
        
        @window.event
        def on_mouse_press(x, y, button, modifiers):
            if not self.current_view:
                return
            
            if hasattr(self.current_view, 'on_mouse_press'):
                result = self.current_view.on_mouse_press(x, y)
                
                if result == 'submit':
                    self.on_submit()
                elif result == 'save':
                    self.save_game()
                    print("Game saved!")
                elif result == 'continue':
                    self.next_day()
    
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
        self.current_day_results.append(scene_result)
        
        # Move to next scene or end of day
        self.state.current_scene_index += 1
        
        if self.state.current_scene_index >= len(self.get_current_day().scenes):
            self.show_day_summary()
        else:
            self.load_current_scene()
    
    def show_day_summary(self):
        """Display end of day summary"""
        self.current_view = DaySummaryView(
            self.current_day_results,
            self.window.width,
            self.window.height
        )
    
    def next_day(self):
        """Move to next day"""
        self.state.day_results.append(self.current_day_results)
        self.current_day_results = []
        self.state.current_day_index += 1
        self.state.current_scene_index = 0
        
        if self.state.current_day_index < len(self.state.days):
            self.load_current_scene()
        else:
            self.show_game_complete()
    
    def show_game_complete(self):
        """Show game completion screen"""
        self.current_view = GameCompleteView(self.window.width, self.window.height)

def main():
    # Create window
    window = pyglet.window.Window(1024, 768, "Day Scene Game")
    
    # Create game
    game = MainGame(window, "game_data")
    
    # Run
    pyglet.app.run()

if __name__ == "__main__":
    main()
