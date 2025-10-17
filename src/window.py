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
        self.list_task_rects = []

        # Icon
        if icon_path:
            try:
                self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 64, 64, True)
                self.set_icon(self.pixbuf)
            except Exception as e:
                self.pixbuf = None
                print(f'Failed to load icon from "{icon_path}": {e}')

        # Colors
        self.dict_colors = {
            1: (1.0, 0.0, 0.0, 1),
            2: (0.0, 0.0, 1.0, 1),
            3: (0.0, 1.0, 0.0, 1),
            4: (1.0, 1.0, 0.0, 1),
            5: (0.5, 0.0, 1.0, 1),
        }

        # Shortcuts
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)

        key, mod = Gtk.accelerator_parse("<Control>q")
        self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, self._on_ctrl_q)

        key, mod = Gtk.accelerator_parse("<Control>s")
        self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, self._on_ctrl_s)


        # Vertical Box
        outerbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(outerbox)

        # Menu Popover
        popover_menu = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        bt = Gtk.ModelButton(label="About GTKScheduling")
        bt.connect("clicked", self._on_click_about)
        vbox.pack_start(bt, False, True, 10)
        vbox.show_all()
        popover_menu.add(vbox)
        popover_menu.set_position(Gtk.PositionType.BOTTOM)

        # Header Bar
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.props.title = "GTKScheduling"
        self.set_titlebar(headerbar)

        # Menu Button
        bt = Gtk.MenuButton(popover=popover_menu)
        icon = Gio.ThemedIcon(name="open-menu-symbolic")
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        bt.add(img_icon)
        headerbar.pack_end(bt)

        # Save button
        bt = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-save-symbolic")
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        bt.add(img_icon)
        bt.connect("clicked", self._on_click_save)
        headerbar.pack_end(bt)

        # Start/Stop button
        bt = Gtk.Button()
        icon_name = "media-playback-pause" if self.app.timer.is_running else "media-playback-start"  
        icon = Gio.ThemedIcon(name=icon_name)
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        bt.add(img_icon)
        bt.connect("clicked", self._on_click_start_stop)
        headerbar.pack_start(bt)

        # Advance button
        bt = Gtk.Button()
        icon = Gio.ThemedIcon(name="go-next")
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        bt.add(img_icon)
        bt.connect("clicked", self._on_click_advance)
        headerbar.pack_start(bt)

        # Slider
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, min=10, max=300, step=1)
        slider.set_draw_value(False)  # Hide the numerical value display
        slider.set_size_request(120, -1)  # Set width
        slider.set_value(self.app.timer.interval_ms)  # Set initial value to match the variable
        slider.connect("value-changed", self._on_slider_value_changed)
        headerbar.pack_start(slider)

        # Stack
        stack = Gtk.Stack()

        # Task Rectangles position parameters
        self.rect_length = 10
        self.rect_x0 = 20 + self.rect_length
        self.rect_y0 = 20
        self.rect_height = 10
        self.lines_dist_y = self.rect_height + 2  # distance between lines
        self.rect_offset_x = self.rect_x0

        # Window dimensions
        win_width = 620
        win_height = self.lines_dist_y*len(self.list_tasks) + 230
        self.set_size_request(win_width, win_height)
        self.set_resizable(True)
        self.set_border_width(6)

        # Diagram Tab
        self.drawingarea_diagram = Gtk.DrawingArea()
        self.drawingarea_diagram.connect("draw", self._on_draw_task_lines_text)
        self.drawingarea_diagram.connect("draw", self._on_draw_task_rects)
        self.drawingarea_diagram.connect("draw", self._on_draw_info)
        self.drawingarea_diagram.connect("button-press-event", self._on_click_task_rect)
        self.drawingarea_diagram.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        drawingarea_width = sum(task.duration for task in list_tasks) * self.rect_length
        drawingarea_height = len(list_tasks) * self.rect_height
        self.drawingarea_diagram.set_size_request(drawingarea_width, drawingarea_height)

        # Scroll
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.drawingarea_diagram)
        stack.add_titled(scrolled_window, "diagram", "Diagram")

        # Info Tab
        self.label_info = Gtk.Label()
        self.refresh_info_label()
        stack.add_titled(self.label_info, "info", "Info")

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

    def _on_ctrl_q(self, accel_group, window, key, modifier):
        self.app.quit()

    def _on_ctrl_s(self, accel_group, window, key, modifier):
        self._open_save_dialog()

    def _on_click_save(self, widget):
        self._open_save_dialog()

    def _open_save_dialog(self):
        dialog = Gtk.FileChooserDialog(title="Save diagram", parent=self, action=Gtk.FileChooserAction.SAVE)
        dialog.set_do_overwrite_confirmation(True)
        dialog.set_current_folder(os.path.expanduser("~"))
        dialog.set_current_name("diagram.png")
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,
        )

        self._add_file_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self._save_diagram_to_png(dialog.get_filename())

        dialog.destroy()

    def _add_file_filters(self, dialog):
        file_filter = Gtk.FileFilter()
        file_filter.set_name("PNG image")
        file_filter.add_mime_type("image/png")
        dialog.add_filter(file_filter)

        file_filter = Gtk.FileFilter()
        file_filter.set_name("Any files")
        file_filter.add_pattern("*")
        dialog.add_filter(file_filter)

    def _on_slider_value_changed(self, scale):
        self.app.timer.interval_ms = scale.get_value()
        self.refresh_info_label()
        self.drawingarea_diagram.queue_draw()

        if self.app.timer.is_running:
            self.app.timer.stop()
            self.app.timer.start()

    def _on_click_start_stop(self, button):
        bt_child = button.get_child()
        if bt_child:
            button.remove(bt_child)

        if self.app.timer.is_running:
            icon_name = "media-playback-start"
            self.app.timer.stop()
        else:
            icon_name = "media-playback-pause"
            self.app.timer.start()

        icon = Gio.ThemedIcon(name=icon_name)
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(img_icon)
        button.show_all()

    def _on_click_advance(self, button):
        self.app.tick()

    def _on_click_outside_popover(self, widget, event):
        # Hide only when clicking in a point that is not the one that opened the popover
        if (self.is_popover_task_active == True and
            event.x != self.cursor_x_at_popover and
            event.y != self.cursor_y_at_popover):
            self.is_popover_task_active = False
            self.popover_task.hide()

    def _on_click_task_rect(self, widget, event):
        if (event.type == Gdk.EventType.BUTTON_PRESS and
            event.button == Gdk.BUTTON_PRIMARY):
            for rect in self.list_task_rects:
                if (rect.x <= event.x <= rect.x + rect.width and
                    rect.y <= event.y <= rect.y + rect.height):
                    self._show_task_popover(rect, widget, event)
                    break

    def _on_click_about(self, widget):
        about = Gtk.AboutDialog(transient_for=self, modal=True)
        about.set_program_name("GTKScheduling")
        about.set_version("0.4.0")
        about.set_comments("CPU scheduling simulator")
        about.set_website("https://github.com/omarelladen/GTKScheduling")
        about.set_website_label("Repository")
        about.set_authors(["Omar El Laden", "Gabriel Martines"])
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_copyright("Copyright © 2025 Omar El Laden")

        if self.pixbuf:
            about.set_logo(self.pixbuf)

        about.connect("response", lambda dialog, response: dialog.destroy())
        about.present()

    def _on_draw_task_lines_text(self, widget, cr: cairo.Context):
        cr.set_source_rgb(0.7,0.7,0.7)
        cr.set_font_size(10)

        for task_num, _ in enumerate(self.list_tasks, 1):
            # Calculate position - offset for single-digit task numbers
            x_pos = 0 if task_num >= 10 else self.rect_x0 / 4
            y_pos = self.rect_y0 + self.lines_dist_y * (task_num - 1) + self.rect_height - 2

            # Draw the task line label
            cr.move_to(x_pos, y_pos)
            cr.show_text(str(task_num))

    def _on_draw_task_rects(self, widget, cr: cairo.Context):
        for rect in self.list_task_rects:
            cr.set_source_rgba(*rect.color)
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.fill()

    def _on_draw_info(self, widget, cr: cairo.Context):
        cr.set_source_rgb(0.7,0.7,0.7)
        cr.set_font_size(10)

        y = self.rect_y0 + self.lines_dist_y * len(self.list_tasks) + 30
        x_offset = self.rect_x0
        spacing = 50

        texts = [
            f"Algorithm: {self.app.scheduler.alg_scheduling}",
            f"CLK period: {self.app.timer.interval_ms:.0f} ms",
            f"Quantum: {self.app.scheduler.quantum}",
            f"Time: {self.app.scheduler.time}",
        ]

        for text in texts:
            cr.move_to(x_offset, y)
            cr.show_text(text)

            extents = cr.text_extents(text)
            x_offset += extents.width + spacing

    def _show_task_popover(self, rect, widget, event):
        self.label_task.set_markup(f"<b>id:</b> {rect.task_record.task.id}\n"
                                   f"<b>start time:</b> {rect.task_record.task.start_time}\n"
                                   f"<b>duration:</b> {rect.task_record.task.duration}\n"
                                   f"<b>priority:</b> {rect.task_record.task.priority}\n"
                                   f"<b>progress:</b> {rect.task_record.progress}\n"
                                   f"<b>progress:</b> {rect.task_record.state}"
        )
        e_x = event.x
        e_y = event.y

        # Set popover position
        self.popover_task.set_relative_to(widget)
        self.popover_task.set_pointing_to(rect)
        self.popover_task.set_position(Gtk.PositionType.TOP)
        self.popover_task.show_all()

        self.cursor_x_at_popover = e_x
        self.cursor_y_at_popover = e_y
        self.is_popover_task_active = True

    def refresh_info_label(self):
        self.label_info.set_markup(
            f"<big><b>Algorithm:</b> {self.app.scheduler.alg_scheduling}</big>\n"
            f"<big><b>Tasks:</b> {len(self.list_tasks)}</big>\n"
            f"<big><b>CLK period:</b> {self.app.timer.interval_ms:.0f} ms</big>\n"
            f"<big><b>Quantum:</b> {self.app.scheduler.quantum}</big>\n"
            f"<big><b>Time:</b> {self.app.scheduler.time}</big>"
        )

    def draw_new_rect(self, current_task):
        # Create Task Rectangles

        for task in self.list_tasks:
            if (task != current_task and
                task.start_time < self.app.scheduler.time and
                not task.state == "running"):
                self.list_task_rects.append(TaskRectangle(self.rect_offset_x - self.rect_length,
                                                          self.rect_y0 + self.lines_dist_y*(task.id-1),
                                                          self.rect_length,
                                                          self.rect_height,
                                                          (0.5, 0.5, 0.5, 0.5),
                                                          TaskRecord(task, task.state, task.progress)))

        self.list_task_rects.append(TaskRectangle(self.rect_offset_x - self.rect_length,
                                                  self.rect_y0 + self.lines_dist_y*(current_task.id-1),
                                                  self.rect_length,
                                                  self.rect_height,
                                                  self.dict_colors[current_task.color_num],
                                                  TaskRecord(current_task, current_task.state, current_task.progress)))
        self.rect_offset_x += self.rect_length

        # Draw created Task Rectangle
        self.drawingarea_diagram.queue_draw()

    def _save_diagram_to_png(self, filename):
        max_x = max(rect.x + rect.width  for rect in self.list_task_rects) if self.list_task_rects else 100
        max_y = max(rect.y + rect.height for rect in self.list_task_rects) if self.list_task_rects else 100

        # Add padding
        surface_width  = int(max_x + self.rect_x0) 
        surface_height = int(max_y + self.rect_y0)

        # Create a Cairo surface
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, surface_width, surface_height)
        cr = cairo.Context(surface)

        # Set background
        cr.set_source_rgb(1,1,1)
        cr.paint()

        # Draw all rectangles
        for rect in self.list_task_rects:
            cr.set_source_rgba(*rect.color)
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.fill()

        # Save to PNG
        try:
            surface.write_to_png(filename)
            surface.finish()
        except Exception as e:
            print(f"Failed to save diagram image at {filename}: {e}")
