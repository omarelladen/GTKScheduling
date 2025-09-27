import os
import csv

import cairo
import gi
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf

from task_rectangle import TaskRectangle
from task_record import TaskRecord


class Window(Gtk.Window):
    def __init__(self,
        app,
        list_tasks,
        icon_path = None,
    ):
        super().__init__()

        self.app = app

        self.list_tasks = list_tasks

        self.dict_colors = {
            1: (1.0, 0.0, 0.0),
            2: (0.0, 0.0, 1.0),
            3: (0.0, 1.0, 0.0),
            4: (1.0, 1.0, 0.0),
            5: (0.5, 0.0, 1.0),
        }

        # Icon
        if icon_path:
            try:
                self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 64, 64, True)
                self.set_icon(self.pixbuf)
            except:
                self.pixbuf = None
                print(f'Failed to load icon from "{icon_path}"')

        # Window dimensions
        self.set_size_request(600, 300)
        self.set_resizable(True)
        self.set_border_width(6)

        # Vertical Box
        outerbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(outerbox)

        # Menu Popover
        popover_menu = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        bt_about = Gtk.ModelButton(label="About GTKScheduling")
        bt_about.connect("clicked", self._on_click_about)
        vbox.pack_start(bt_about, False, True, 10)
        vbox.show_all()
        popover_menu.add(vbox)
        popover_menu.set_position(Gtk.PositionType.BOTTOM)

        # Header Bar
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.props.title = "GTKScheduling"
        self.set_titlebar(headerbar)

        # Menu Button
        bt_menu = Gtk.MenuButton(popover=popover_menu)
        icon = Gio.ThemedIcon(name="open-menu-symbolic")
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        bt_menu.add(img_icon)
        headerbar.pack_end(bt_menu)

        # Stack
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        # Task Rectangles position parameters
        self.scale_rect = 10
        self.rect_line_x0 = 20 + self.scale_rect  # initial x
        self.rect_line_y0 = 20  # initial y
        self.rect_height = 10  # bar height
        self.rect_lines_dist = self.rect_height + 2  # distance between lines
        self.rect_dist = 0  #1  # distance between 2 bars
        self.rect_offset = self.rect_line_x0  # initial offset that will be incremented with time (+= 1*scale_rect)

        self.list_rect_progress_bar = []

        # Bars Tab
        self.drawingarea_progress_bar = Gtk.DrawingArea()
        self.drawingarea_progress_bar.connect("draw", self._on_draw_text)
        self.drawingarea_progress_bar.connect("draw", self._on_draw_progress_bar)
        self.drawingarea_progress_bar.connect("button-press-event", self._on_click_task_rect)
        self.drawingarea_progress_bar.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        stack.add_titled(self.drawingarea_progress_bar, "diagram", "Diagram")

        # Stats Tab
        self.label_stats = Gtk.Label()
        self._refresh_stats_label()
        stack.add_titled(self.label_stats, "stats", "Statistics")

        # Task Popover
        self.popover_task = Gtk.Popover()
        self.label_task = Gtk.Label()
        self.popover_task.add(self.label_task)

        self.is_popover_task_active = False
        self.cursor_x_at_popover = None
        self.cursor_y_at_popover = None

        # All clicks will be checked to be able to hide the task popovers
        self.connect("button-press-event", self._on_click_outside_popover)

        # Stack Switcher
        stackswitcher = Gtk.StackSwitcher()
        stackswitcher.set_stack(stack)
        stackswitcher.set_halign(Gtk.Align.CENTER)  # horizontal

        outerbox.pack_start(stackswitcher, False, True, 0)
        outerbox.pack_start(stack, True, True, 0)
            
    def _on_click_outside_popover(self, widget, event):
        if (self.is_popover_task_active == True and
            event.x != self.cursor_x_at_popover and
            event.y != self.cursor_y_at_popover):
            self.is_popover_task_active = False
            self.popover_task.hide()

    def _on_click_task_rect(self, widget, event):
        if (event.type == Gdk.EventType.BUTTON_PRESS and
            event.button == Gdk.BUTTON_PRIMARY):
            for rect in self.list_rect_progress_bar:
                if (rect.x <= event.x <= rect.x + rect.width and
                    rect.y <= event.y <= rect.y + rect.height):
                    self._show_task_popover(rect, widget, event)
                    break

    def _on_click_about(self, widget):
        about = Gtk.AboutDialog(transient_for=self, modal=True)

        about.set_program_name("GTKScheduling")
        about.set_version("0.1.0")
        about.set_comments("CPU scheduling simulator")
        about.set_website("https://github.com/omarelladen/GTKScheduling")
        about.set_website_label("Repository")
        about.set_authors(["Omar El Laden"])
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_copyright("Copyright © 2025 Omar El Laden")

        if self.pixbuf:
            about.set_logo(self.pixbuf)

        about.connect("response", lambda dialog, response: dialog.destroy())
        about.present()

    def _on_draw_text(self, widget, cr: cairo.Context):
        cr.set_source_rgb(1, 1, 1)
        cr.set_font_size(10)

        for task_num, _ in enumerate(self.list_tasks, 1):
            # Calculate position - offset for single-digit task numbers
            num_pos = 0 if task_num >= 10 else self.rect_line_x0 / 4
            x_pos = num_pos
            y_pos = self.rect_line_y0 + self.rect_lines_dist * (task_num - 1) + self.rect_height - 2

            # Draw the task line label
            cr.move_to(x_pos, y_pos)
            cr.show_text(str(task_num))
            
    def _on_draw_progress_bar(self, widget, cr: cairo.Context):
        for rect in self.list_rect_progress_bar:
            cr.set_source_rgb(*rect.color)
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)

            cr.fill()

    def _show_task_popover(self, rect, widget, event):
        self.label_task.set_markup(f"<b>id:</b> {rect.task_record.task.id}\n"
                                   f"<b>start time:</b> {rect.task_record.task.start_time}\n"
                                   f"<b>duration:</b> {rect.task_record.task.duration}\n"
                                   f"<b>priority:</b> {rect.task_record.task.priority}\n"
                                   f"<b>progress:</b> {rect.task_record.progress}")
        e_x = event.x
        e_y = event.y

        # Set popover position
        self.popover_task.set_relative_to(widget)
        self.popover_task.set_pointing_to(rect)
        self.popover_task.set_position(Gtk.PositionType.TOP)
        self.popover_task.show_all()

        # Set current popover location and state so that it is gets hiden only by clicking outside this point
        self.cursor_x_at_popover = e_x
        self.cursor_y_at_popover = e_y
        self.is_popover_task_active = True
            
    def _refresh_stats_label(self):
        self.label_stats.set_markup(
            f"<big><b>Algorithm:</b> {self.app.scheduler.alg_scheduling}</big>\n"
            f"<big><b>Tasks:</b> {len(self.list_tasks)}</big>\n"
            f"<big><b>CLK duration:</b> {self.app.timer.interval_ms} ms</big>\n"
            f"<big><b>Quantum:</b> {self.app.scheduler.quantum} CLKs</big>\n"
        )
     
    def update_rect_time(self, current_task):
        # Create Task Rectangles
        task_num = current_task.id
        length = 1 * self.scale_rect
        num_pos = 0 if task_num >= 10 else self.rect_line_x0 / 4
        color = self.dict_colors[current_task.color_num]
        self.list_rect_progress_bar.append(TaskRectangle(self.rect_offset - (length-self.rect_dist),
                                                         self.rect_line_y0 + self.rect_lines_dist*(task_num-1),
                                                         length-self.rect_dist,
                                                         self.rect_height,
                                                         color,
                                                         TaskRecord(current_task, current_task.state, current_task.progress )))
        self.rect_offset += (1 * self.scale_rect)

        # Draw created Task Rectangle
        self.drawingarea_progress_bar.queue_draw()
