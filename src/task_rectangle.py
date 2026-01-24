import gi
from gi.repository import Gdk

class TaskRectangle(Gdk.Rectangle):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        color_rgba,
        task_record = None,
    ):
        # Inherited:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.color_rgba = color_rgba
        self.task_record = task_record
