# main.py
import pyglet
from pyglet.window import key
from src.game_architecture import DaySceneGame
from src.ui import SceneView, DaySummaryView, GameCompleteView

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
