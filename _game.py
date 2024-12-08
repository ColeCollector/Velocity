from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import Ellipse, Rectangle, Color, RoundedRectangle
from kivy.uix.screenmanager import Screen
import json
import random

WIDTH = 360
HEIGHT = 640

class LevelScreen(Screen):
    def __init__(self, **kwargs):
        super(LevelScreen, self).__init__(**kwargs)
        self.level = 1
        self.completed = []
        self.scroll_view = None
        
        with self.canvas:
            # Draw background
            Color(0.9, 0.9, 0.9, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)

            Color(0.8, 0.8, 0.8, 1)
            for b in range(3):
                Ellipse(pos=(WIDTH / 2 - 37 + b * 30, 100), size=(14, 14))

            Color(1, 1, 1, 1)
            self.page_number = Ellipse(pos=(WIDTH / 2 - 37 , 100), size=(14, 14))

        # Bind size and position changes to update the background
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Create and manually position title text
        self.title_label = Label(
            text="Levels",
            font_size=40,
            font_name="assets/ASHBW___.ttf",
            size_hint=(None, None),
            size=(360, 50),
            color=(0.7, 0.7, 0.7, 1),
            pos=(0, 500),
        )
        self.add_widget(self.title_label)

        # Add scrollable level menu
        self.create_scrollable_level_menu()

    def update(self, dt):
        page_number = max(0, min(int(self.scroll_view.scroll_x * 3), 2))
        self.page_number.pos = (WIDTH / 2 - 37 + page_number*30, 100)

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def create_scrollable_level_menu(self):
        # Create a horizontal BoxLayout to hold multiple grids
        scroll_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), spacing=50)
        scroll_layout.size = (1220, 400)  # Adjust the total width as needed
        scroll_layout.pos = (15, 120)   # Position in the middle of the screen

        self.buttons = {}

        # Add grids to the layout
        for page in range(3):
            grid = GridLayout(cols=5, rows=5, spacing=15, padding=10, size_hint=(None, None))
            grid.size = (360, 360)

            for level in range(1 + page * 25, 26 + page * 25 ):
                button = Button(
                    text=str(level),
                    font_name="assets/ASHBM___.ttf",
                    size_hint=(None, None),
                    size=(50, 50),
                    color= (1, 1, 1, 1),
                    background_normal='',
                    background_color=(0.8, 0.8, 0.8, 1),
                )
                button.bind(on_press=lambda btn, lvl=level: self.select_level(lvl))
                self.buttons[level] = button
                grid.add_widget(button)

            scroll_layout.add_widget(grid)

        # Wrap the BoxLayout in a ScrollView
        self.scroll_view = ScrollView(size_hint=(None, None), size=(400, 400), pos=(15, 120))
        self.scroll_view.bar_width = 0
        self.scroll_view.add_widget(scroll_layout)
        self.add_widget(self.scroll_view)

    def on_enter(self, *args):
        sm = self.manager
        game_screen = sm.get_screen("game")
        self.completed = game_screen.completed

        for level, button in self.buttons.items():
            if level in self.completed:
                # Update completed levels
                button.background_normal = 'assets/check.png'
                button.text = ''  # Remove text if needed
            else:
                # Update uncompleted levels (optional if the state hasn't changed)
                button.background_normal = ''
                button.text = str(level)

        self.scroll_view.scroll_x = 0
        Clock.schedule_interval(self.update, 1 / 60)  # 60 FPS

    def on_leave(self, *args):
        Clock.unschedule(self.update)
    
    def select_level(self, level):
        self.level = level
        self.manager.current = "game"

class GameScreen(Screen):
    ball_y = NumericProperty(50)  # Ball's vertical position
    ball_velocity = NumericProperty(0)  # Ball's current velocity
    gravity = NumericProperty(-0.5)  # Gravity force
    jump_strength = NumericProperty(10)  # Jump strength
    bounciness = NumericProperty(0.8)  # Bounciness factor
    level = NumericProperty(1)  # level
    counter = NumericProperty(0) # Frame counter
    ground_touches = NumericProperty(0) # Number of times the ball has touched the ground
    trail = ListProperty([]) # Trailing balls
    completed  = ListProperty([]) # Completed levels
    obstacles = ListProperty([]) # White rectangles
    
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.menu_moving_down = False  
        self.hit = False
        self.sound = {"level_up" : SoundLoader.load('assets/level_up1.wav'), "kick" : SoundLoader.load('assets/kick.wav')}
        self.sound["level_up"].volume = 0.5
        self.sound["kick"].volume = 0.1

        self.init_canvas()
        self.dynamic_canvas = Widget()
        self.add_widget(self.dynamic_canvas)
        self.bind(on_touch_down=self.on_touch)

    def init_canvas(self):
        """Initialize the visual elements of the game."""
        with self.canvas:
            Color(0.75, 0.75, 0.75, 1)
            self.background_rect = Rectangle(pos=(0, 0), size=(WIDTH, HEIGHT))
            
            # Draw the target height rectangle
            Color(1.0, 1.0, 0.0, 0.5)
            self.target_rect = Rectangle(pos=(0, 0), size=(WIDTH, 70))

            # Draw the height peak rectangle
            self.height_color = Color(1, 0, 0, 0.5)
            self.height_rect = Rectangle(pos=(0, -50), size=(WIDTH, 20))

            # Draw the obstacle rectangle
            self.load_level()

            # Draw the ball
            Color(0.45, 0.45, 0.45, 1)  
            self.ball = Ellipse(pos=(180 - 15, self.ball_y), size=(30, 30))

            # Draw the ground 
            Color(1, 1, 1, 1)
            self.ground = RoundedRectangle(pos=(25, 35), size=(WIDTH - 50, 15), radius = [10] * 4)

            # Draw the level at the top
            self.init_level_label()

            # Draw the menu rectangle
            Color(0.9, 0.9, 0.9, 1) 
            self.menu = Rectangle(pos=(0, HEIGHT), size=(360, 60))

            self.menu_button = Button(
                size_hint=(None, None),
                size=(40, 40),
                pos=(10, HEIGHT + 10),
                background_normal='assets/menu_button.png',
                on_press=lambda instance: setattr(self.manager, 'current', 'title'),
            )
            self.add_widget(self.menu_button)

            self.reset_button = Button(
                size_hint=(None, None),
                size=(40, 40),
                pos=(60, HEIGHT + 10),
                background_normal='assets/reset_button.png',
                on_press=self.reset,
            )
            self.add_widget(self.reset_button)

            self.level_button = Button(
                size_hint=(None, None),
                size=(40, 40),
                pos=(110, HEIGHT + 10),
                background_normal='assets/level_button.png',
                on_press=lambda instance: setattr(self.manager, 'current', 'level'),
            )
            self.add_widget(self.level_button)

    def init_level_label(self):
        """Initialize the level label at the top of the screen."""
        self.level_label = Label(
            text=f"{self.level}",
            font_size=60,
            font_name="assets/ASHBW___.ttf",
            color=(1, 1, 1, 1),
            size_hint=(None, None),
        )
        self.level_label.x = (WIDTH - self.level_label.width) / 2
        self.level_label.top = HEIGHT - 10  # Set 10px from the top
        self.add_widget(self.level_label)

    def on_touch(self, instance, touch):
        """Make the ball jump when the screen is tapped."""
        if touch.y > HEIGHT * 0.9:
            self.menu_moving_down = True
        else:
            self.menu_moving_down = False
            self.ball_velocity = self.jump_strength
            self.ground_touches = 0
            self.hit = False

    def reset(self, instance):
        """Reset the ball position and velocity"""
        self.ball_y = 150
        self.ball_velocity = 0

    def load_level(self):
        # Load level data
        with open("level_data.json", "r") as file:
            level_data = json.load(file)

        level_info = level_data.get(str(self.level), {})
        self.target_rect.pos = level_info.get("target_rect", (0, 0))

        # Clear existing obstacles
        for rect_data in self.obstacles:
            self.canvas.remove(rect_data["rect"])
            self.canvas.remove(rect_data["color"])
        self.obstacles.clear()

        # Generate obstacles
        obstacles = level_info.get("obstacle_rect", [(25, -15, None)])  # Default to one stationary obstacle
        with self.canvas:
            for x, y, obstacle_type in obstacles:
                color = Color(1, 1, 1, 1)
                obstacle_width = WIDTH - 250 if obstacle_type == "moving" else WIDTH - 50
                rect = RoundedRectangle(pos=(x, y), size=(obstacle_width, 15), radius=[10] * 4)
                
                # Add obstacle to the list with relevant properties
                self.obstacles.append({
                    "rect": rect,
                    "width": obstacle_width,
                    "color": color,
                    "type": obstacle_type,
                    "velocity": random.choice([-3, 3]) if obstacle_type == "moving" else 0
                })

    def on_enter(self):
        """Retrieve level from level menu."""
        Clock.schedule_interval(self.update, 1 / 60)  # 60 FPS
        self.reset(None)
        self.height_rect.pos = (0, -50)
        sm = self.manager
        level_screen = sm.get_screen("level")
        self.level = level_screen.level
        self.level_label.text = f"{self.level}"
        self.load_level()

    def on_leave(self):
        Clock.unschedule(self.update)

    def increment_level(self):
        """Increment the level and update the label."""
        self.sound["level_up"].play()
        self.completed.append(self.level)
        self.level += 1
        self.level_label.text = f"{self.level}"
        self.load_level()

    def add_trail(self):
        """Add the current ball position to the trail."""
        self.trail.append({"pos": (180, self.ball_y + 15), "opacity": 0.5, "size": 30})  # Centered
        if len(self.trail) > 10:  # Limit trail length
            self.trail.pop(0)

    def render_trail(self):
        """Render the ball's trail."""
        self.dynamic_canvas.canvas.clear()
        with self.dynamic_canvas.canvas:
            for trail_point in self.trail[::-1]:
                Color(0.45, 0.45, 0.45, trail_point["opacity"])  # Semi-transparent red
                Ellipse(pos=(trail_point["pos"][0] - trail_point["size"] / 2, trail_point["pos"][1] - trail_point["size"] / 2), size=(trail_point["size"], trail_point["size"]))

                if self.trail.index(trail_point) > 5:
                    trail_point["opacity"] -= 0.05

                trail_point["size"] -= 0.5

    def update(self, dt):
        """Update the ball's position and velocity."""
        # Gravity
        self.ball_velocity += self.gravity
        self.ball_y += self.ball_velocity
        
        # Check for collision with the ground
        if self.ball_y < 50:  # Ground level is 50
            self.ground_touches += 1
            self.ball_y = 50
            self.ball_velocity = -self.ball_velocity * self.bounciness

        self.height_color.a = max(0, self.height_color.a - (1 / 120))

        for obstacle in self.obstacles:
            if obstacle['type'] == 'ghost':
                obstacle['color'].a = 1 if self.ground_touches == 1 else 0.5
    
            elif obstacle['type'] == 'moving':
                if obstacle['rect'].pos[0] > WIDTH - obstacle["width"] / 2:
                    obstacle["velocity"] = -3

                elif obstacle['rect'].pos[0] < - obstacle["width"] * 0.5 :
                    obstacle["velocity"] = 3

                obstacle['rect'].pos = (obstacle['rect'].pos[0] + obstacle["velocity"], obstacle['rect'].pos[1])

            # Check for collision with the obstacle
            if obstacle['color'].a == 1:
                obstacle_top = obstacle['rect'].pos[1] + 15
                obstacle_bottom = obstacle['rect'].pos[1]
                next_frame = self.ball_y + self.ball_velocity + self.gravity

                if (WIDTH / 2 > obstacle['rect'].pos[0]) and (WIDTH / 2 < obstacle['rect'].pos[0] + obstacle["width"]):
                    # Bounce off the top
                    if (self.ball_y + 0.5 >= obstacle_top and next_frame - 25 <= obstacle_bottom and self.ball_velocity <= 0):
                        self.ball_y = obstacle_top
                        self.ball_velocity = -self.ball_velocity * self.bounciness
                        self.hit = True

                    # Bounce off the bottom
                    elif (self.ball_y < obstacle_top and next_frame + 25 > obstacle_bottom and self.ball_velocity > 0):
                        self.ball_y = obstacle_bottom - 25
                        self.ball_velocity = -self.ball_velocity * self.bounciness
                        self.hit = True

        if round(self.ball_velocity) == 0 and self.ball_velocity > 0 and (self.ground_touches == 1 or self.hit):
            self.height_rect.pos = (0, self.ball_y)
            self.height_color.a = 0.5
            self.hit = False 

            if self.ball_y >= self.target_rect.pos[1] and self.ball_y + 20 <= self.target_rect.pos[1] + 70 and self.level < 50:
                self.increment_level()

        # Menu rectangle logic
        self.menu_buttons = [self.menu, self.menu_button, self.reset_button, self.level_button]

        if self.menu_moving_down:
            self.line_hit_counter += 1
            if self.menu.pos[1] > 580: 
                for button in self.menu_buttons:
                    button.pos = (button.pos[0], button.pos[1] - 2)

            elif self.line_hit_counter >= 180:  # After 3 seconds, close the menu
                self.menu_moving_down = False
                self.line_hit_counter = 0
        else:
            self.line_hit_counter = 0
            if self.menu.pos[1] < HEIGHT: 
                for button in self.menu_buttons:
                    button.pos = (button.pos[0], button.pos[1] + 2)

        self.counter += 1
        # Add a trail every second frame
        if self.counter % 2 == 0:
            self.add_trail()

        self.ball.pos = (WIDTH / 2 - 15, self.ball_y)
        self.render_trail()

if __name__ == "__main__":
    import _main