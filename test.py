from kivy.app import App
from kivy.uix.button import Button
from kivy.graphics import Rectangle
from kivy.core.image import Image

class ScalableButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load the image and get the texture
        try:
            self.image = Image('assets/level_button.png')  # Correct image path
            if not self.image.texture:
                print("Failed to load texture!")
            self.texture = self.image.texture
        except Exception as e:
            print(f"Error loading image: {e}")

        # Make the button background transparent
        self.background_normal = ''
        
        # Bind to the button's size and update the texture accordingly
        self.bind(size=self.update_texture)

    def update_texture(self, *args):
        """Update the texture size when the button size changes."""
        if self.texture is None:
            print("No texture found!")
            return

        # Create a new texture that fits the button's size
        texture = self.texture
        texture = texture.create(size=(self.width, self.height))  # Resize the texture
        
        # Blit the image data into the new texture
        texture.blit_buffer(self.image.pixels, colorfmt='rgba', bufferfmt='ubyte')

        # Clear the previous canvas and draw the updated texture
        self.canvas.before.clear()
        with self.canvas.before:
            self.rect = Rectangle(texture=self.texture, pos=self.pos, size=self.size)

class MyApp(App):
    def build(self):
        # Create an instance of the ScalableButton
        button = ScalableButton(text="Click Me", size_hint=(None, None), size=(200, 100))
        button.pos = (100, 100)  # Set the position of the button
        return button

if __name__ == '__main__':
    MyApp().run()
