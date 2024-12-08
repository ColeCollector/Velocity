from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Rectangle, Color
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
import math


class BallGame(Widget):
    ball_y = NumericProperty(200)  # Original ball's vertical position
    ball_velocity = NumericProperty(0)  # Original ball's velocity
    falling_ball_y = NumericProperty(600)  # Second ball's vertical position
    falling_ball_velocity = NumericProperty(0)  # Second ball's velocity
    gravity = NumericProperty(-0.5)  # Gravity force
    jump_strength = NumericProperty(10)  # Jump strength
    bounciness = NumericProperty(0.7)  # Bounciness factor

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ball = None  # Original ball graphic
        self.falling_ball = None  # Falling ball graphic
        self.ground = None  # Ground graphic
        self.background_rect = None  # Semi-transparent background rectangle
        self.init_canvas()
        Clock.schedule_interval(self.update, 1 / 60)  # 60 FPS
        Window.size = (360, 640)  # Set window size for mobile testing

    def init_canvas(self):
        """Initialize the visual elements of the game."""
        with self.canvas:
            # Draw the semi-transparent background rectangle
            Color(0.2, 0.2, 0.2, 0.5)  # Gray with 50% transparency
            self.background_rect = Rectangle(pos=(50, 150), size=(260, 340))
            
            # Draw the original ball (red circle)
            Color(1, 0, 0, 1)  # Red color, fully opaque
            self.ball = Ellipse(pos=(180, self.ball_y), size=(50, 50))
            
            # Draw the falling ball (blue circle)
            Color(0, 0, 1, 1)  # Blue color, fully opaque
            self.falling_ball = Ellipse(pos=(180, self.falling_ball_y), size=(50, 50))
            
            # Draw the ground (green rectangle)
            Color(0, 1, 0, 1)  # Green color, fully opaque
            self.ground = Rectangle(pos=(0, 0), size=(Window.width, 50))

    def on_touch_down(self, touch):
        """Make the original ball jump when the screen is tapped."""
        self.ball_velocity = self.jump_strength

    def update(self, dt):
        """Update the balls' positions and velocities."""
        # Update gravity for the original ball
        self.ball_velocity += self.gravity
        self.ball_y += self.ball_velocity



        # Collision with the ground for the original ball
        if self.ball_y < 50:  # Ground level is 50
            self.ball_y = 50
            self.ball_velocity = -self.ball_velocity * self.bounciness

        if self.falling_ball:
            # Update gravity for the falling ball
            self.falling_ball_velocity += self.gravity
            self.falling_ball_y += self.falling_ball_velocity

            # Collision with the ground for the falling ball
            if self.falling_ball_y < 50:  # Ground level is 50
                self.falling_ball_y = 50
                self.falling_ball_velocity = -self.falling_ball_velocity * self.bounciness
            self.falling_ball.pos = (180, self.falling_ball_y)

            # Collision detection between the two balls
            self.check_ball_collision()

        # Update the visual positions of the balls
        self.ball.pos = (180, self.ball_y)
        

    def check_ball_collision(self):
        """Check and handle collisions between the two balls."""
        ball_radius = 25  # Radius of each ball (size / 2)
        distance = abs(self.ball_y - self.falling_ball_y)

        if distance <= ball_radius * 2:  # Collision detected
            # Exchange velocities for a simple elastic collision effect
            self.ball_velocity, self.falling_ball_velocity = (
                self.falling_ball_velocity,
                self.ball_velocity,
            )
            print("1")
            self.canvas.remove(self.falling_ball)
            self.falling_ball = None


class JumpGameApp(App):
    def build(self):
        return BallGame()


if __name__ == '__main__':
    JumpGameApp().run()
