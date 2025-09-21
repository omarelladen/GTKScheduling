import gi
from gi.repository import Gdk

class Rectangle(Gdk.Rectangle):
    def __init__(self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        caption: int = 0,
        color: tuple[float, float, float] = (0.0, 0.8, 0.0)
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.caption = caption
        self.color = color
