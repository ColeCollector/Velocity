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
from _settings import WIDTH, HEIGHT, MULTIPLIER
import json, math


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
            for i in range(3):
                Ellipse(pos=(WIDTH / 2 - 37 + i * 30, 100), size=(14, 14))

            Color(1, 1, 1, 1)
            self.page_number = Ellipse(pos=(WIDTH / 2 - 37 , 100), size=(14, 14))

            #self.init_label()

        # Bind size and position changes to update the background
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Create and manually position title text
        self.title_label = Label(
            text="Levels",
            font_size=40 * MULTIPLIER,
            font_name="assets/ASHBW___.ttf",
            size_hint=(None, None),
            size=(360 * MULTIPLIER, 50 * MULTIPLIER),
            color=(0.7, 0.7, 0.7, 1),
            pos=(0, 500 * MULTIPLIER),
        )
        self.add_widget(self.title_label)

        # Add scrollable level menu
        self.create_scrollable_level_menu()

    def init_label(self):
        self.completed_label = Label(
            text=f"{len(self.completed)}",
            font_size=30 * MULTIPLIER,
            font_name="assets/ASHBW___.ttf",
            color=(1, 1, 1, 1),
            size_hint=(None, None),
        )
        self.completed_label.x = 0
        self.completed_label.top = HEIGHT
        self.add_widget(self.completed_label)

    def update(self, dt):
        page_number = max(0, min(int(self.scroll_view.scroll_x * 3), 2))
        self.page_number.pos = (WIDTH / 2 - 37 + page_number*30, 100)

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def create_scrollable_level_menu(self):
        # Create a horizontal BoxLayout to hold multiple grids
        scroll_layout = BoxLayout(orientation="horizontal", size_hint=(None, None), spacing=50)
        scroll_layout.size = (1220 * MULTIPLIER, 400 * MULTIPLIER)  # Adjust the total width as needed
        scroll_layout.pos = (15 * MULTIPLIER, 120 * MULTIPLIER)   # Position in the middle of the screen

        self.buttons = {}

        # Add grids to the layout
        for page in range(3):
            grid = GridLayout(cols=5, rows=5, spacing=15 * MULTIPLIER, padding=10 * MULTIPLIER, size_hint=(None, None))
            grid.size = (360 * MULTIPLIER, 360 * MULTIPLIER)

            for level in range(1 + page * 25, 26 + page * 25 ):
                button = Button(
                    border=(0,0,0,0),
                    text=str(level),
                    font_size= 15 * MULTIPLIER,
                    font_name="assets/ASHBM___.ttf",
                    size_hint=(None, None),
                    size=(50 * MULTIPLIER, 50 * MULTIPLIER),
                    color= (1, 1, 1, 1),
                    background_normal="",
                    background_color=(0.8, 0.8, 0.8, 1),
                )
                button.bind(on_press=lambda btn, lvl=level: self.select_level(lvl))
                self.buttons[level] = button
                grid.add_widget(button)

            scroll_layout.add_widget(grid)

        # Wrap the BoxLayout in a ScrollView
        self.scroll_view = ScrollView(size_hint=(None, None), size=(400 * MULTIPLIER, 400 * MULTIPLIER), pos=(15 * MULTIPLIER, 120 * MULTIPLIER))
        self.scroll_view.bar_width = 0
        self.scroll_view.add_widget(scroll_layout)
        self.add_widget(self.scroll_view)

    def on_enter(self, *args):
        sm = self.manager
        game_screen = sm.get_screen("game")
        self.completed = game_screen.completed
        #self.completed_label.text = f"{len(self.completed)}"
        for level, button in self.buttons.items():
            if level in self.completed:
                # Update completed levels
                button.background_normal = "assets/check.png"
                button.text = ""  # Remove text if needed
                button.background_color = (1.0, 1.0, 1.0, 1)

            elif (math.floor(len(self.completed) / 25) + 1) * 25 < level:
                button.background_normal = "assets/lock.png"
                button.text = str(level)
                button.background_color = (0.8, 0.8, 0.8, 1)

            else:
                button.background_normal = ""
                button.text = str(level)
                button.background_color = (0.8, 0.8, 0.8, 1)

        self.scroll_view.scroll_x = 0
        Clock.schedule_interval(self.update, 1 / 60)  # 60 FPS

    def on_leave(self, *args):
        Clock.unschedule(self.update)
    
    def select_level(self, level):
        if (math.floor(len(self.completed) / 25) + 1) * 25 >= level or True:
            self.level = level
            self.manager.current = "game"

class GameScreen(Screen):
    ball_size = 40 * MULTIPLIER
    ball_y = ListProperty([100, 100])  # Ball"s vertical position
    ball_x = ListProperty([WIDTH / 4 - ball_size / 2, WIDTH / 4 * 3 - ball_size / 2]) 
    ball_velocity = ListProperty([0, 0])  # Ball"s current velocity
    gravity = NumericProperty(-0.5 * MULTIPLIER)  # Gravity force
    jump_strength = NumericProperty(10 * MULTIPLIER)  # Jump strength
    bounciness = NumericProperty(0.8)  # Bounciness factor
    level = NumericProperty(1)  # level
    counter = NumericProperty(0) # Frame counter
    ground_touches = ListProperty([0, 0]) # Number of times the ball has touched the ground
    trail = ListProperty([]) # Trailing balls
    completed  = ListProperty([]) # Completed levels
    obstacles = ListProperty([]) # White rectangles
    
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.menu_moving_down = False  
        self.hit = [False, False]
        self.sound = {"level_up" : SoundLoader.load("assets/level_up1.wav"), "kick" : SoundLoader.load("assets/kick.wav")}
        self.sound["level_up"].volume = 0.5
        self.sound["kick"].volume = 0.1

        self.init_canvas()
        self.dynamic_canvas = Widget()
        self.add_widget(self.dynamic_canvas)
        self.bind(on_touch_down=self.on_touch)

    def init_canvas(self):
        """Initialize the visual elements of the game."""
        with self.canvas:
            Color(0.8, 0.8, 0.8, 1)
            self.left_half = Rectangle(pos=(0, 0), size=(WIDTH / 2, HEIGHT))
            
            Color(0.9, 0.9, 0.9, 1)
            self.right_half = Rectangle(pos=(WIDTH / 2, 0), size=(WIDTH / 2, HEIGHT))

            # Draw the target height rectangle
            Color(1.0, 1.0, 0.0, 0.5)
            self.target_rect = Rectangle(pos=(0, 0), size=(WIDTH, 70 * MULTIPLIER))

            # Draw the height peak rectangle
            self.height_color = Color(0.85, 0, 0.2, 0.5)  
            self.height_rect = Rectangle(pos=(0, -50), size=(WIDTH, 20 * MULTIPLIER))

            # Draw the obstacle rectangle
            self.load_level()

            # Draw the ball
            Color(0.85, 0, 0.2, 1)  
            self.ball1 = Ellipse(pos=(self.ball_x[0], self.ball_y[0]), size=(self.ball_size, self.ball_size))
            self.ball2 = Ellipse(pos=(self.ball_x[1], self.ball_y[1]), size=(self.ball_size, self.ball_size))

            # Draw the level at the top
            self.init_level_label()
            
            # Draw the menu rectangle
            Color(0.93, 0.93, 0.93, 1) 
            self.menu = Rectangle(pos=(0, HEIGHT), size=(360 * MULTIPLIER, 60 * MULTIPLIER))

            self.menu_button = Button(
                border=(0,0,0,0),
                size_hint=(None, None),
                size=(40 * MULTIPLIER, 40 * MULTIPLIER),
                pos=(10 * MULTIPLIER, HEIGHT + 10 * MULTIPLIER),
                background_normal="assets/menu_button.png",
                on_press=lambda instance: setattr(self.manager, "current", "title"),
            )
            self.add_widget(self.menu_button)

            self.reset_button = Button(
                border=(0,0,0,0),
                size_hint=(None, None),
                size=(40 * MULTIPLIER, 40 * MULTIPLIER),
                pos=(60 * MULTIPLIER, HEIGHT + 10 * MULTIPLIER),
                background_normal="assets/reset_button.png",
                on_press=self.reset,
            )
            self.add_widget(self.reset_button)

            self.level_button = Button(
                border=(0,0,0,0),
                size_hint=(None, None),
                size=(40 * MULTIPLIER, 40 * MULTIPLIER),
                pos=(110 * MULTIPLIER, HEIGHT + 10 * MULTIPLIER),
                background_normal="assets/level_button.png",
                on_press=lambda instance: setattr(self.manager, "current", "level"),
            )
            self.add_widget(self.level_button)

    def init_level_label(self):
        """Initialize the level label at the top of the screen."""
        self.level_label = Label(
            text=f"{self.level}",
            font_size=60 * MULTIPLIER,
            font_name="assets/ASHBW___.ttf",
            color=(1, 1, 1, 1),
            size_hint=(None, None),
        )
        self.level_label.x = (WIDTH - self.level_label.width) / 2
        self.level_label.top = HEIGHT - 10 * MULTIPLIER # Set 10px from the top
        self.add_widget(self.level_label)

    def on_touch(self, instance, touch):
        """Make the ball jump when the screen is tapped."""
        if touch.y > HEIGHT * 0.9:
            self.menu_moving_down = True
        else:
            if touch.x < WIDTH / 2:
                self.ball_velocity[0] = self.jump_strength
                self.ground_touches[0] = 0
                self.hit[0] = False
            else:
                self.ball_velocity[1] = self.jump_strength
                self.ground_touches[1] = 0
                self.hit[1] = False

            self.menu_moving_down = False
            
            for obstacle in self.obstacles:
                self.collision(obstacle)

    def reset(self, instance):
        """Reset the ball position and velocity"""
        pass
        #self.ball_y = 150
        #self.ball_velocity = 0

    def load_level(self):
        # Load level data
        with open("level_data.json", "r") as file:
            level_data = json.load(file)

        level_info = level_data.get(str(self.level), {})
        self.target_rect.pos = (level_info.get("target_rect", (0, 0))[0] * MULTIPLIER,
                                level_info.get("target_rect", (0, 0))[1] * MULTIPLIER)

        # Clear existing obstacles
        for rect_data in self.obstacles:
            self.canvas.remove(rect_data["rect"])
            self.canvas.remove(rect_data["color"])
        self.obstacles.clear()

        # Generate obstacles
        obstacles = level_info.get("obstacle_rect", [(25, -15, None, None)])  # Default to one stationary obstacle
        with self.canvas:

            color = Color(1, 1, 1, 1)
            rect = RoundedRectangle(pos=(25 * MULTIPLIER, 35 * MULTIPLIER), size=(WIDTH - 50 * MULTIPLIER, 15 * MULTIPLIER), radius = [10 * MULTIPLIER] * 4)
            self.obstacles.append({
                "rect": rect,
                "size": [WIDTH - 50 * MULTIPLIER, 15 * MULTIPLIER],
                "color": color,
                "type": "ground",
                "velocity": 0
            })

            for x, y, obstacle_type, velocity in obstacles:
                
                obstacle_width = WIDTH - 50 * MULTIPLIER if obstacle_type in ["ghost"] else WIDTH - 250 * MULTIPLIER 
                obstacle_height = 15 * MULTIPLIER 
                if obstacle_type == "bouncy":   color = Color(1, 0.5, 0.72, 1)
                else:                           color = Color(1, 1, 1, 1)

                rect = RoundedRectangle(pos=(x * MULTIPLIER, y * MULTIPLIER), size=(obstacle_width, obstacle_height), radius=[10 * MULTIPLIER] * 4)
                
                # Add obstacle to the list with relevant properties
                self.obstacles.append({
                    "rect": rect,
                    "size": [obstacle_width, obstacle_height],
                    "color": color,
                    "type": obstacle_type,
                    "velocity": velocity
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

        if self.level not in self.completed:
            self.completed.append(self.level)

        if self.level < 75:
            self.ground_touches = [0, 0]
            self.level += 1
            self.level_label.text = f"{self.level}"
            self.load_level()

    def add_trail(self):
        """Add the current ball position to the trail."""
        if len(self.trail) > 15:  # Limit trail length
            self.trail.pop(0)
            self.trail.pop(0)

        for i in range(2):
            self.trail.append({"pos": (self.ball_x[i] + self.ball_size / 2, self.ball_y[i] + self.ball_size / 2), "opacity": 0.5, "size": self.ball_size})  # Centered

    def render_trail(self):
        """Render the ball"s trail."""
        self.dynamic_canvas.canvas.clear()
        with self.dynamic_canvas.canvas:
            for trail_point in self.trail[::-1]:
                Color(0.85, 0, 0.2, trail_point["opacity"])
                Ellipse(pos=(trail_point["pos"][0] - trail_point["size"] / 2, trail_point["pos"][1] - trail_point["size"] / 2), size=(trail_point["size"], trail_point["size"]))

                if self.trail.index(trail_point) > 5:
                    trail_point["opacity"] -= 0.05

                trail_point["size"] -= 0.5
    
    def collision(self, obstacle):
        if obstacle["color"].a == 1:
            for i in range(2):
                obstacle_bounciness = 1.3 if  obstacle["type"] == "bouncy" else self.bounciness
                obstacle_top = obstacle["rect"].pos[1] + obstacle["size"][1]
                obstacle_bottom = obstacle["rect"].pos[1] - self.ball_size
                next_frame = self.ball_y[i] + self.ball_velocity[i] + self.gravity 
                
                if obstacle["rect"].pos[0] - self.ball_size < self.ball_x[i] < obstacle["rect"].pos[0] + obstacle["size"][0]:
                    # Bounce off the top
                    if (self.ball_y[i] + 0.5 * MULTIPLIER >= obstacle_top and next_frame <= obstacle_top and self.ball_velocity[i] <= 0):
                        self.ball_y[i] = obstacle_top
                        self.ball_velocity[i] *= -obstacle_bounciness
                        self.ground_touches[i] += 1

                    # Bounce off the bottom
                    elif (self.ball_y[i] <= obstacle_bottom and next_frame >= obstacle_bottom and self.ball_velocity[i] > 0):
                        self.ball_y[i] = obstacle_bottom
                        self.ball_velocity[i] *= -obstacle_bounciness
                        
                        if obstacle["type"] == "ground": self.ground_touches[i] += 1
                        else: self.hit[i] = True

                elif obstacle["type"] == "switch":
                    if self.ball_y[i] > obstacle["rect"].pos[1] - self.ball_size and self.ball_y[i] < obstacle["rect"].pos[1] + obstacle["size"][1] and self.ball_velocity[i] > 0:
                        if obstacle["velocity"] == 0:
                            obstacle["velocity"] = -5 + 10*i

    def update(self, dt):
        """Update the ball"s position and velocity."""
        # Gravity
        for i in range(2):
            self.ball_velocity[i] = max(min(self.ball_velocity[i], 20 * MULTIPLIER), -20 * MULTIPLIER)
            self.ball_velocity[i] += self.gravity
            self.ball_y[i] = min(self.ball_y[i] + self.ball_velocity[i], HEIGHT - self.ball_size / 2)

        self.height_color.a = max(0, self.height_color.a - (1 / 120))

        for obstacle in self.obstacles:
            if obstacle["type"] == "ghost":
                obstacle["color"].a = 1 if 1 in self.ground_touches else 0.5
    
            elif obstacle["type"] in ["moving", "bouncy", "switch"]:
                obstacle["rect"].pos = (obstacle["rect"].pos[0] + obstacle["velocity"], obstacle["rect"].pos[1])
                if obstacle["type"] == "switch":
                    if (obstacle["rect"].pos[0] + 35 * MULTIPLIER > WIDTH - obstacle["size"][0] or obstacle["rect"].pos[0] < 35 * MULTIPLIER):
                        obstacle["velocity"] = 0
                else:
                    if (obstacle["rect"].pos[0] + 35 * MULTIPLIER > WIDTH - obstacle["size"][0] / 2) or (obstacle["rect"].pos[0] < - obstacle["size"][0] / 2 + 35 * MULTIPLIER):
                        obstacle["velocity"] *= -1

            # Check for collision with the obstacle
            self.collision(obstacle)

        for i in range(2):
            if round(self.ball_velocity[i] / MULTIPLIER) == 0 and self.ball_velocity[i] > 0 and (self.ground_touches[i] == 1 or self.hit[i]):
                self.height_rect.pos = (0, self.ball_y[i])
                self.height_color.a = 0.5
                self.hit[i] = False 

                if self.ball_y[i] >= self.target_rect.pos[1] and self.ball_y[i] + 20 * MULTIPLIER <= self.target_rect.pos[1] + 70 * MULTIPLIER:
                    self.increment_level()
                break

        # Menu rectangle logic
        self.menu_buttons = [self.menu, self.menu_button, self.reset_button, self.level_button]

        if self.menu_moving_down:
            self.line_hit_counter += 1
            if self.menu.pos[1] >  HEIGHT - 60 * MULTIPLIER: 
                for button in self.menu_buttons:
                    button.pos = (button.pos[0], button.pos[1] - 2 * MULTIPLIER)

            elif self.line_hit_counter >= 180:  # After 3 seconds, close the menu
                self.menu_moving_down = False
                self.line_hit_counter = 0
        else:
            self.line_hit_counter = 0
            if self.menu.pos[1] < HEIGHT: 
                for button in self.menu_buttons:
                    button.pos = (button.pos[0], button.pos[1] + 2)

        # Add a trail every second frame
        if self.counter % 2 == 0:
            self.add_trail()
        
        self.counter += 1
        self.ball1.pos = (self.ball_x[0], self.ball_y[0])
        self.ball2.pos = (self.ball_x[1], self.ball_y[1])
        self.render_trail()

if __name__ == "__main__":
    import _main