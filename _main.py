from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.graphics import Rectangle, Color
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from _game import LevelScreen, GameScreen
from _settings import WIDTH, HEIGHT, MULTIPLIER

# Set the window size
Window.size = (WIDTH, HEIGHT)
Window.orientation = "portrait"

# To-do
# - audio slider
# - improved level screen
# - shadows
# - Maybe add other falling balls? that are ontop of each other or side by side 


# Title Screen
class TitleScreen(Screen):
    def __init__(self, **kwargs):
        super(TitleScreen, self).__init__(**kwargs)
        self.sound = SoundLoader.load("assets/click.wav")
        self.sound.volume = 0.1
        with self.canvas:
            # Draw background
            Color(0.1, 0.1, 0.1, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)

        # Bind size and position changes to update the background
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Create and manually position title text
        self.title_label = Label(
            text="Velocity",
            font_size=40 * MULTIPLIER,
            font_name="assets/ASHBW___.ttf",
            size_hint=(None, None),
            size=(300, 50),
            pos=(WIDTH / 2 - 150, 400 * MULTIPLIER),
        )
        self.add_widget(self.title_label)

        # Create and manually position play button
        self.play_button = Button(
            text="Play",
            font_size=15 * MULTIPLIER,
            size_hint=(None, None),
            size=(200 * MULTIPLIER, 50 * MULTIPLIER),
            pos=(WIDTH / 2 - 100 * MULTIPLIER, 300 * MULTIPLIER),
            on_press=self.start_game,
        )
        self.add_widget(self.play_button)

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def start_game(self, instance):
        self.manager.current = "game"
        self.sound.play()


# Main App
class VelocityApp(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(TitleScreen(name="title"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(LevelScreen(name="level"))
        return sm


VelocityApp().run()
