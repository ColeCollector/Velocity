from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Ellipse, Rectangle, Color, RoundedRectangle
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
import random

Window.clearcolor = (0.7, 0.7, 0.7, 1)  # Set the background to light gray

WIDTH = 360
HEIGHT = 640

# To-do
# - Add shadows
# - Maybe add other falling balls? that are ontop of each other or side by side 
# - Add transparent blocks that become collidable when you pass through them

class BallGame(Widget):
    ball_y = NumericProperty(50)  # Ball's vertical position
    ball_velocity = NumericProperty(0)  # Ball's current velocity
    gravity = NumericProperty(-0.5)  # Gravity force
    jump_strength = NumericProperty(10)  # Jump strength
    bounciness = NumericProperty(0.8)  # Bounciness factor
    score = NumericProperty(0)  # Score
    counter = NumericProperty(0) # Frame counter
    trail = [] # Trailing balls
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ball = None
        self.ground = None 
        self.height_rect = None
        self.target_rect = None
        self.ground_touches = 1
        self.init_canvas()
        
        self.init_score_label()
        Clock.schedule_interval(self.update, 1 / 60)  # 60 FPS
        Window.size = (360, 640)  # Set window size for mobile testing

    def init_canvas(self):
        """Initialize the visual elements of the game."""
        with self.canvas:
            # Draw the target height rectangle
            Color(1.0, 1.0, 0.0, 0.5)
            self.target_rect = Rectangle(pos=(0, 0), size=(WIDTH, 70))
            self.reset_target()

            # Draw the height peak rectangle
            Color(1, 0, 0, 0.5)
            self.height_rect = Rectangle(pos=(0, -50), size=(WIDTH, 20))

            # Draw the ball
            Color(0.45, 0.45, 0.45, 1) 
            self.ball = Ellipse(pos=(180, self.ball_y), size=(30, 30))
            
            # Draw the ground 
            Color(1, 1, 1, 1)
            self.ground = RoundedRectangle(pos=(25, 35), size=(WIDTH - 50, 15), radius = [10] * 4)

    def init_score_label(self):
        """Initialize the score label at the top of the screen."""
        self.score_label = Label(
            text=f"{self.score}",
            font_size="60sp",
            font_name="ASHBW___.ttf",
            color=(1, 1, 1, 1),  # White text
            size_hint=(None, None),
        )
        self.score_label.x = (WIDTH - self.score_label.width) / 2
        self.score_label.top = Window.height - 10  # Set 10px from the top
        self.add_widget(self.score_label)

    def on_touch_down(self, touch):
        """Make the ball jump when the screen is tapped."""
        self.ball_velocity = self.jump_strength
        self.ground_touches = 0
        
    def increment_score(self):
        """Increment the score and update the label."""
        self.score += 1
        self.score_label.text = f"{self.score}"

    def reset_target(self, *args):
        rnum = (random.randint(150, HEIGHT - 200))

        while abs(rnum - self.target_rect.pos[1]) <= 25:
            rnum = (random.randint(150, HEIGHT - 200))

        self.target_rect.pos = (0, rnum)

    def add_trail(self):
        """Add the current ball position to the trail."""
        self.trail.append({"pos": (180, self.ball_y + 15), "opacity": 0.5, "size": 30})  # Centered
        if len(self.trail) > 10:  # Limit trail length
            self.trail.pop(0)

    def render_trail(self):
        """Render the ball's trail."""
        self.canvas.before.clear()
        with self.canvas.before:
            for trail_point in self.trail:
                Color(0.45, 0.45, 0.45, trail_point["opacity"])  # Semi-transparent red
                Ellipse(pos=(trail_point["pos"][0] - trail_point["size"]/2, trail_point["pos"][1] - trail_point["size"]/2), size=(trail_point["size"], trail_point["size"]))
                if self.trail.index(trail_point) > 5:
                    trail_point["opacity"] -= 0.05  # Fade out
                trail_point["size"] -= 0.5
                
    def update(self, dt):
        """Update the ball's position and velocity."""
        # Apply gravity to ball's velocity
        self.ball_velocity += self.gravity
        # Update the ball's position
        self.ball_y += self.ball_velocity

        # Check for collision with the ground
        if self.ball_y < 50:  # Ground level is 50
            self.ground_touches += 1
            self.ball_y = 50
            self.ball_velocity = -self.ball_velocity * self.bounciness


        # Update the visual position of the ball
        self.ball.pos = (WIDTH/2 - 15, self.ball_y)

        if round(self.ball_velocity) == 0 and self.ball_velocity > 0:
            if self.ground_touches == 1 : 
                self.height_rect.pos = (self.height_rect.pos[0], self.ball_y)

                if self.ball_y >= self.target_rect.pos[1] and self.ball_y + 20 <= self.target_rect.pos[1] + 70:
                    self.increment_score()
                    Clock.schedule_once(self.reset_target, 0.4)

                # Move the target after 0.5 seconds
                
        self.counter += 1
        if self.counter % 2 == 0:
            self.add_trail()

        # Render the trail
        self.render_trail()

class JumpGameApp(App):
    def build(self):
        return BallGame()

if __name__ == '__main__':
    JumpGameApp().run()