"""
Chicken Jump Game
A simple wall-jumping game where a chicken bounces between walls avoiding spikes.
"""

from kivy.app import App
from kivy.core.window import Window

from widgets.game_manager import GameManager

class GameApp(App):
    """Main application class"""

    def build(self):
        # Set window properties
        Window.clearcolor = (0.05, 0.05, 0.15, 1)
        Window.size = (1000, 700)

        # Create and return game widget
        game = GameManager()
        return game


if __name__ == "__main__":
    GameApp().run()