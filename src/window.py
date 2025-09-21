import os
import csv

import gi
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf

from rectangle import Rectangle


class Window(Gtk.Window):
    def __init__(self, 
        icon_file: str = '',
        app = None,
        list_tasks = [],
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
        try:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_file, 64, 64, True)
            self.set_icon(self.pixbuf)
        except:
            self.pixbuf = None
            print(f'Failed to load icon from "{icon_file}"')

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
        bt_about = Gtk.ModelButton(label="About GTK Scheduling")
        bt_about.connect("clicked", self._on_click_about)
        vbox.pack_start(bt_about, False, True, 10)
        vbox.show_all()
        popover_menu.add(vbox)
        popover_menu.set_position(Gtk.PositionType.BOTTOM)

        # Header Bar
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.props.title = "GTK Scheduling"
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

        # Create Progress Bars Rectangles
        self.scale_rect = 10
        self.pb_line_x0 = 14 + self.scale_rect  # initial x
        self.pb_line_y0 = 20  # initial y
        self.pb_height = 10  # bar height
        self.pb_lines_dist = self.pb_height + 2  # distance between lines
        self.pb_dist = 0  #1  # distance between 2 bars
        self.list_rect_progress_bar = []
        self.pb_offset = self.pb_line_x0  # inial offset that will be incremented with time (+= 1*scale_rect)
        for task_num in range(1, len(self.list_tasks) + 1):
            num_pos = 0 if task_num >= 10 else self.pb_line_x0/4
            self.list_rect_progress_bar.append(Rectangle(num_pos,
                                                         self.pb_height + self.pb_line_y0 + self.pb_lines_dist*(task_num-1),
                                                         0,
                                                         0,
                                                         f"Line {task_num}"))

        # Progress Bar Tab
        self.drawingarea_progress_bar = Gtk.DrawingArea()
        self.drawingarea_progress_bar.connect("draw", self._on_draw_progress_bar)
        self.drawingarea_progress_bar.connect("button-press-event", self._on_click_progress_bar)
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

    def _on_click_progress_bar(self, widget, event):
        if (event.type == Gdk.EventType.BUTTON_PRESS and
            event.button == Gdk.BUTTON_PRIMARY):
            for rect in self.list_rect_progress_bar:
                if (rect.x <= event.x <= rect.x + rect.width and
                    rect.y <= event.y <= rect.y + rect.height and
                    isinstance(rect.caption, int)):
                    self._show_task_popover(rect, widget, event)
                    break


    def _on_click_about(self, widget):
        about = Gtk.AboutDialog(transient_for=self, modal=True)

        about.set_program_name("GTK Scheduling")
        about.set_version("0.1.0")
        about.set_comments("CPU scheduling simulator")
        about.set_website("https://github.com/omarelladen/GTK-Scheduling")
        about.set_website_label("Repository")
        about.set_authors(["Omar El Laden"])
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_copyright("Copyright © 2025 Omar El Laden")

        if self.pixbuf:
            about.set_logo(self.pixbuf)

        about.connect("response", lambda dialog, response: dialog.destroy())
        about.present()


    def _on_draw_progress_bar(self, widget, cr):
        for rect in self.list_rect_progress_bar:
            cr.set_source_rgb(*rect.color)
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)

            # Line indication
            if isinstance(rect.caption, str) and "Line" in rect.caption:
                cr.show_text(rect.caption.replace("Line ", ""))

            cr.fill()

    def _show_task_popover(self, rect, widget, event):
        self.label_task.set_text(f"id: {rect.caption}\n"
                                 f"start time: {self.list_tasks[rect.caption-1].start_time}\n"
                                 f"duration: {self.list_tasks[rect.caption-1].duration}\n"
                                 f"priority: {self.list_tasks[rect.caption-1].priority}\n"
                                 f"progress: {self.list_tasks[rect.caption-1].progress}\n"
                                 f"state: {self.list_tasks[rect.caption-1].state}")

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
            f"<big><b>Algorithm:</b> {self.app.alg_scheduling}</big>\n"
            f"<big><b>Tasks:</b> {len(self.list_tasks)}</big>\n"
            f"<big><b>CLK duration:</b> {self.app.clk_duration} ms</big>\n"
            f"<big><b>Quantum:</b> {self.app.quantum} CLKs</big>\n"
        )
     
    def update_rect_time(self, current_task):
        # Create Progress Bars Rectangles
        task_num = current_task.id
        length = 1 * self.scale_rect  # current_task.duration * self.scale_rect
        num_pos = 0 if task_num >= 10 else self.pb_line_x0/4
        color = self.dict_colors[current_task.color_num]
        self.list_rect_progress_bar.append(Rectangle(self.pb_offset - (length-self.pb_dist),
                                                     self.pb_line_y0 + self.pb_lines_dist*(task_num-1),
                                                     length-self.pb_dist,
                                                     self.pb_height,
                                                     task_num,
                                                     color))
        self.pb_offset += (1 * self.scale_rect)

        # Draw created rectangle
        self.drawingarea_progress_bar.queue_draw()
