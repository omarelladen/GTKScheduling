import gi
from gi.repository import Gdk

class TaskRectangle(Gdk.Rectangle):
    def __init__(self,
        x,
        y,
        width,
        height,
        color: tuple[float, float, float] = (1, 1, 1),
        task_record = None,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.color = color
        self.task_record = task_record
