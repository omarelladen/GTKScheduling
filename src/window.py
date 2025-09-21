import os
import csv

import gi
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf

from rectangle import Rectangle


class Window(Gtk.Window):
    def __init__(self, 
        icon_file: str = '',
        app = None,
        list_tasks = []
    ):
        super().__init__()
        
        self.app = app

        self.list_tasks = list_tasks

        # Icon
        try:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_file, 64, 64, True)
            self.set_icon(self.pixbuf)
        except:
            self.pixbuf = None
            print(f'Failed to load icon from "{icon_file}"')

        # Window dimensions
        self.set_size_request(580, 550)
        self.set_resizable(False)
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

        dict_colors = {
            1: (1.0, 0.0, 0.0),
            2: (0.0, 0.0, 1.0),
            3: (0.0, 1.0, 0.0),
            4: (1.0, 1.0, 0.0),
            5: (0.5, 0.0, 1.0),
        }

        # Create Progress Bars Rectangles
        pb_line_x0 = 14  # initial x
        pb_line_y0 = 20  # initial y
        pb_height = 10  # bar height
        pb_lines_dist = pb_height + 2  # distance between lines
        pb_dist = 1  # distance between 2 bars
        scale_rect = 10
        self.list_rect_progress_bar = []
        for task in self.list_tasks:
            task_num = task.id
            length = task.duration * scale_rect
            num_pos = 0 if task_num >= 10 else pb_line_x0/4
            color = dict_colors[task.color_num]
            # self.list_rect_progress_bar.append(Rectangle(num_pos, pb_height + pb_line_y0 + pb_lines_dist*(task_num-1), 0, 0, f"Line {task_num}"))
            pb_offset = pb_line_x0
            self.list_rect_progress_bar.append(Rectangle(pb_offset - (length-pb_dist), pb_line_y0 + pb_lines_dist*(task_num-1), length-pb_dist, pb_height, task_num, color))
            pb_offset += length

        # Progress Bar Tab
        self.drawingarea_progress_bar = Gtk.DrawingArea()
        self.drawingarea_progress_bar.connect("draw", self._on_draw_progress_bar)
        self.drawingarea_progress_bar.connect("button-press-event", self._on_click_progress_bar)
        self.drawingarea_progress_bar.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        stack.add_titled(self.drawingarea_progress_bar, "bars", "Bars")



        # Stats Tab
        self.label_stats = Gtk.Label()
        self._refresh_stats_label()
        stack.add_titled(self.label_stats, "stats", "Statistics")

        # Chapter Popover
        self.popover_chapter = Gtk.Popover()
        self.label_chapter = Gtk.Label()
        self.popover_chapter.add(self.label_chapter)

        self.is_popover_chapter_active = False
        self.cursor_x_at_popover = None
        self.cursor_y_at_popover = None

        # All clicks will be checked to be able to hide the chapter popovers
        self.connect("button-press-event", self._on_click_outside_popover)

        # Stack Switcher
        stackswitcher = Gtk.StackSwitcher()
        stackswitcher.set_stack(stack)
        stackswitcher.set_halign(Gtk.Align.CENTER)  # horizontal

        outerbox.pack_start(stackswitcher, False, True, 0)
        outerbox.pack_start(stack, True, True, 0)

    def _on_click_outside_popover(self, widget, event):
        if (self.is_popover_chapter_active == True and
            event.x != self.cursor_x_at_popover and
            event.y != self.cursor_y_at_popover):
            self.is_popover_chapter_active = False
            self.popover_chapter.hide()

    def _on_click_progress_bar(self, widget, event):
        if (event.type == Gdk.EventType.BUTTON_PRESS and
            event.button == Gdk.BUTTON_PRIMARY):
            for rect in self.list_rect_progress_bar:
                if (rect.x <= event.x <= rect.x + rect.width and
                    rect.y <= event.y <= rect.y + rect.height and
                    isinstance(rect.caption, int)):
                    self._show_chapter_popover(rect, widget, event)
                    break


    def _on_click_about(self, widget):
        about = Gtk.AboutDialog(transient_for=self, modal=True)

        about.set_program_name("GTK Scheduling")
        about.set_version("0.0.1")
        about.set_comments("CPU Scheduling simulator")
        about.set_website("https://github.com/omarelladen")
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

    def _show_chapter_popover(self, rect, widget, event):
        self.label_chapter.set_text(f"{rect.caption}")

        e_x = event.x
        e_y = event.y

        # Set popover position
        self.popover_chapter.set_relative_to(widget)
        self.popover_chapter.set_pointing_to(rect)
        self.popover_chapter.set_position(Gtk.PositionType.TOP)
        self.popover_chapter.show_all()

        # Set current popover location and state so that it is gets hiden only by clicking outside this point
        self.cursor_x_at_popover = e_x
        self.cursor_y_at_popover = e_y
        self.is_popover_chapter_active = True
            
    def _refresh_stats_label(self):
        self.label_stats.set_markup(
            f"<big><b>Tasks:</b> {self.app.num_tasks}</big>\n"
            f"<big><b>CLK duration:</b> {self.app.clk_duration} ms</big>\n"
            f"<big><b>Quantum:</b> {self.app.quantum} CLKs</big>\n"
        )
        
     
    def update_rect_time(self, current_task):
        for rect in self.list_rect_progress_bar:
            if "Line" not in str(rect.caption) and rect.caption == current_task:
                rect.x += 10
                self.drawingarea_progress_bar.queue_draw()
