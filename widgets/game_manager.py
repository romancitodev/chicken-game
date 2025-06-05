from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import (
    Color,
    Ellipse,
    Rectangle,
    Triangle,
    Line
)
from kivy.core.window import Window
import math
from .score_manager import ScoreManager
from .character import Chicken
from .obstacles_manager import SpikeGenerator

class GameManager(Widget):
    """Main game widget containing all game logic and rendering"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize game components
        self.chicken = None
        self.spike_generator = None
        self.score_manager = ScoreManager()
        self.game_over = False
        self.paused = False
        self.current_score = 0
        self.best_score = 0

        # Create score label with proper setup
        self.score_label_widget = Label(
            text="0",
            font_size="48sp",
            color=(1, 1, 1, 1),  # White text
            pos=(self.width/2, self.height),
            size=(160, 60),
            halign='center',
            valign='middle'
        )
        self.score_label_widget.text_size = self.score_label_widget.size
        
        # Add score label to widget
        self.add_widget(self.score_label_widget)

        self.pause_layout = None
        self.game_over_layout = None

        # Bind to window size changes and input
        self.bind(size=self.on_size_change) #type: ignore
        Window.bind(on_key_down=self.on_key_down)

        # Start game loop
        Clock.schedule_interval(self.update, 1.0 / 60.0)

        # Initialize when widget is ready
        Clock.schedule_once(self.initialize_game, 0)

    def initialize_game(self, _):
        """Initialize game components"""
        if self.size[0] > 0 and self.size[1] > 0:
            self.reset_game()

    def on_size_change(self, _, size):
        if size[0] > 0 and size[1] > 0:
            # Update score label position
            self.score_label_widget.center_x = size[0] / 2
            self.score_label_widget.top = size[1] - 20
            self.reset_game()

    def on_key_down(self, _, key, *__):
        """Handle keyboard input"""
        # Space bar (32) or Up arrow (273) to jump
        if key in [32, 273] and self.chicken and not self.game_over and not self.paused:
            self.chicken.jump()
        # R key to restart
        elif key == 114 and self.game_over:  # 'r' key
            self.reset_game()
        # P key or Escape to pause/unpause
        elif key in [112, 27] and not self.game_over:  # 'p' key or Escape
            self.paused = not self.paused
            self.update_pause_menu()
        return True

    def on_touch_down(self, touch):
        """Handle touch input for jumping and restarting"""
        if self.game_over:
            self.reset_game()
        elif self.paused:
            self.paused = False
            self.update_pause_menu()
        elif self.chicken:
            self.chicken.jump()
        return True

    def reset_game(self):
        """Reset game to initial state"""
        # Remove any existing overlays
        self.clear_overlays()
        
        # Initialize chicken at center
        if self.width > 0 and self.height > 0:
            center_x = self.width / 2
            center_y = self.height / 2
            self.chicken = Chicken(center_x, center_y)

            # Initialize spike generator
            self.spike_generator = SpikeGenerator(self.width, self.height)

            # Reset game state
            self.score_manager.reset_current_score()
            self.game_over = False
            self.paused = False
            self.update_score_display()
            
            # Update score label position
            self.score_label_widget.center_x = self.width / 2
            self.score_label_widget.top = self.height - 20

    def update_score_display(self):
        """Update the score display"""
        self.score_label_widget.text = str(self.score_manager.current_score)

    def clear_overlays(self):
        """Clear pause and game over overlays"""
        if self.pause_layout:
            self.remove_widget(self.pause_layout)
            self.pause_layout = None
        if self.game_over_layout:
            self.remove_widget(self.game_over_layout)
            self.game_over_layout = None

    def update_pause_menu(self):
        """Update pause menu visibility"""
        if self.paused:
            self.show_pause_menu()
        else:
            if self.pause_layout:
                self.remove_widget(self.pause_layout)
                self.pause_layout = None

    def update(self, dt):
        """Main game update loop"""
        if self.game_over:
            if not self.game_over_layout:
                self.show_game_over()
            return
            
        if self.paused or not self.chicken or not self.spike_generator:
            return

        # Update chicken
        (wall_hit, coords) = self.chicken.update(dt, (self.width, self.height))

        # Check if chicken hit a wall
        if wall_hit:
            self.score_manager.add_point()
            self.update_score_display()

            # Generate new level on EVERY wall hit
            self.spike_generator.regenerate_spikes(
                coords, self.score_manager.difficulty_level
            )

        # Check spike collisions
        if self.spike_generator.check_collisions(self.chicken):
            self.chicken.alive = False

        # Check if chicken died
        if not self.chicken.alive:
            self.game_over = True

        # Redraw game elements (but not UI)
        self.draw_game()

    def draw_game(self):
        """Draw all game elements"""
        if not self.canvas:
            return
        # Clear only the main canvas, not the entire widget
        self.canvas.clear()
        
        with self.canvas:
            # Background
            Color(0.05, 0.05, 0.15)  # Dark blue background
            Rectangle(pos=(0, 0), size=self.size)

            # Draw decorative center orb
            self.draw_center_orb()

            # Draw vertical walls (visual reference)
            self.draw_walls()

            # Draw spikes
            self.draw_spikes()

            # Draw chicken
            if self.chicken and self.chicken.alive:
                self.draw_chicken()
        
        # Ensure score is on top by removing and re-adding it
        if self.score_label_widget in self.children:
            self.remove_widget(self.score_label_widget)
        self.add_widget(self.score_label_widget)

    def draw_walls(self):
        """Draw vertical walls as visual reference"""
        Color(0.15, 0.15, 0.25, 0.8)  # Slightly lighter than background

        # Left wall
        Rectangle(pos=(0, 0), size=(5, self.height))

        # Right wall
        Rectangle(pos=(self.width - 5, 0), size=(5, self.height))

    def draw_chicken(self):
        """Draw the chicken character"""
        if not self.chicken:
            return

        # Chicken body (yellow circle)
        Color(1, 0.9, 0.2)  # Bright yellow
        Ellipse(
            pos=(
                self.chicken.pos.x - self.chicken.radius,
                self.chicken.pos.y - self.chicken.radius,
            ),
            size=(self.chicken.size, self.chicken.size),
        )

        # Chicken beak (orange triangle)
        Color(1, 0.5, 0)  # Orange
        beak_size = 8
        direction = 1 if self.chicken.velocity.x > 0 else -1
        beak_x = self.chicken.pos.x + (self.chicken.radius * direction * 0.7)
        beak_y = self.chicken.pos.y

        # Draw beak as small triangle
        if direction > 0:  # Facing right
            points = [
                beak_x,
                beak_y - 3,
                beak_x,
                beak_y + 3,
                beak_x + beak_size,
                beak_y,
            ]
        else:  # Facing left
            points = [
                beak_x,
                beak_y - 3,
                beak_x,
                beak_y + 3,
                beak_x - beak_size,
                beak_y,
            ]

        Triangle(points=points)

        # Eyes
        Color(0, 0, 0)  # Black
        eye_size = 3
        eye_offset = 4
        Ellipse(
            pos=(self.chicken.pos.x - eye_offset, self.chicken.pos.y + 2),
            size=(eye_size, eye_size),
        )

    def draw_center_orb(self):
        """Draw decorative center orb"""
        # Pulsing effect
        pulse = abs(math.sin(Clock.get_time() * 2)) * 0.3 + 0.7

        # Main orb
        Color(0.2, 0.3, 0.5, 0.4 * pulse)
        orb_size = 500 + (self.score_manager.current_score * 2)
        orb_x = self.width / 2 - orb_size / 2
        orb_y = self.height / 2 - orb_size / 2
        Ellipse(pos=(orb_x, orb_y), size=(orb_size, orb_size))
        
        # Inner glow
        Color(0.3, 0.4, 0.7, 0.6 * pulse)
        inner_size = orb_size * 0.6
        inner_x = self.width / 2 - inner_size / 2
        inner_y = self.height / 2 - inner_size / 2
        Ellipse(pos=(inner_x, inner_y), size=(inner_size, inner_size))

        # Core
        Color(0.5, 0.6, 0.9, 0.8 * pulse)
        core_size = orb_size * 0.3
        core_x = self.width / 2 - core_size / 2
        core_y = self.height / 2 - core_size / 2
        Ellipse(pos=(core_x, core_y), size=(core_size, core_size))

    def draw_spikes(self):
        """Draw all spikes as proper triangles"""
        if not self.spike_generator:
            return
        Color(0.2, 0.2, 0.3)  # Dark gray-blue spikes that match background

        for spikes in self.spike_generator.spikes:
            for spike in spikes:
                points = spike.get_triangle_points()
                Triangle(points=points)

                # Add a slightly darker outline for definition
                Color(0.15, 0.15, 0.2)
                Line(points=points + [points[0], points[1]], width=1.2)
                Color(0.2, 0.2, 0.3)  # Reset to spike color

    def show_pause_menu(self):
        """Show pause menu overlay"""
        if self.pause_layout or not hasattr(self.pause_layout, 'canvas'):
            return
            
        self.pause_layout = FloatLayout(size=self.size)

        # Dark overlay
        with self.pause_layout.canvas: #type: ignore
            Color(0, 0, 0, 0.7)
            Rectangle(pos=(0, 0), size=self.size)

            # Menu box
            box_width, box_height = 400, 200
            box_x = self.width / 2 - box_width / 2
            box_y = self.height / 2 - box_height / 2

            Color(0.15, 0.2, 0.3, 0.95)
            Rectangle(pos=(box_x, box_y), size=(box_width, box_height))

            Color(1, 1, 1, 1)
            Line(rectangle=(box_x, box_y, box_width, box_height), width=2)

        # Title
        pause_title = Label(
            text="PAUSA",
            font_size='40sp',
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(300, 50),
            pos=(self.width / 2 - 150, self.height / 2 + 60)
        )
        self.pause_layout.add_widget(pause_title)

        # Instructions
        pause_instructions = Label(
            text="Pulsa [P] o [ESC] para continuar",
            font_size='20sp',
            color=(0.8, 0.8, 0.9, 1),
            size_hint=(None, None),
            size=(300, 40),
            pos=(self.width / 2 - 150, self.height / 2 + 10)
        )
        self.pause_layout.add_widget(pause_instructions)

        pause_touch = Label(
            text="Toca la pantalla para seguir o R para reiniciar",
            font_size='18sp',
            color=(0.7, 0.7, 0.9, 1),
            size_hint=(None, None),
            size=(400, 30),
            pos=(self.width / 2 - 200, self.height / 2 - 30)
        )
        self.pause_layout.add_widget(pause_touch)

        self.add_widget(self.pause_layout)

    def show_game_over(self):
        """Show game over overlay"""
        if self.game_over_layout:
            return
            
        self.game_over_layout = FloatLayout(size=self.size)

        # Dark red overlay
        with self.game_over_layout.canvas: # type: ignore
            Color(0.9, 0.2, 0.2, 0.7)
            Rectangle(pos=(0, 0), size=self.size)

        # Game over text
        game_over_label = Label(
            text=f"GAME OVER\nScore: {self.score_manager.current_score}\nBest: {self.score_manager.high_score}\n\nTap to restart or press R",
            font_size='24sp',
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(400, 200),
            pos=(self.width / 2 - 200, self.height / 2 - 100)
        )
        game_over_label.text_size = (400, 200)
        self.game_over_layout.add_widget(game_over_label)

        self.add_widget(self.game_over_layout)