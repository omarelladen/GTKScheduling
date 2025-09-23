import gi
from gi.repository import Gdk

class Rectangle(Gdk.Rectangle):
    def __init__(self,
        x,
        y,
        width,
        height,
        caption = '',
        color: tuple[float, float, float] = (1, 1, 1)
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.caption = caption
        self.color = color
