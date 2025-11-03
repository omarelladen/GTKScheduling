import os
import csv
import cairo
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf

from .task_rectangle import TaskRectangle
from .task_record import TaskRecord

class Window(Gtk.Window):
    def __init__(self,
        app,
        list_tasks,
        app_icon_path = None,
        play_icon = None,
        pause_icon = None,
        next_icon = None,
        skip_icon = None,
        restart_icon = None,
        menu_icon = None,
        save_icon = None,
        edit_icon = None,
    ):
        super().__init__()

        # References the main application and task list
        self.app = app
        self.list_tasks = list_tasks
        
        self.app_icon_path = app_icon_path

        # Icon names
        self.play_icon = play_icon
        self.pause_icon = pause_icon
        self.next_icon = next_icon
        self.skip_icon = skip_icon
        self.restart_icon = restart_icon
        self.menu_icon = menu_icon
        self.save_icon = save_icon
        self.edit_icon = edit_icon

        # List of TaskRectangle objects for drawing
        self.list_task_rects = []

        # Set the app icon from file
        if self.app_icon_path:
            try:
                self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.app_icon_path, 64, 64, True)
                self.set_icon(self.pixbuf)
            except Exception as e:
                self.pixbuf = None
                print(f'Failed to load icon from "{self.app_icon_path}": {e}')

        # Task Colors
        self.dict_colors = {
            0:  (0.0, 0.8, 0.8, 1),  # turquoise
            1:  (1.0, 0.0, 0.0, 1),  # red
            2:  (0.0, 0.0, 1.0, 1),  # blue
            3:  (0.0, 1.0, 0.0, 1),  # green
            4:  (1.0, 1.0, 0.0, 1),  # yellow
            5:  (0.5, 0.0, 1.0, 1),  # purple
            6:  (1.0, 0.5, 0.0, 1),  # orange
            7:  (0.0, 1.0, 1.0, 1),  # cyan
            8:  (1.0, 0.0, 1.0, 1),  # magenta
            9:  (0.6, 0.3, 0.0, 1),  # brown
            10: (0.0, 0.5, 0.5, 1),  # teal
            11: (0.3, 0.3, 0.3, 1),  # dark grey
            12: (0.7, 0.7, 0.7, 1),  # light grey
            13: (0.8, 0.2, 0.4, 1),  # dark pink
            14: (0.2, 0.8, 0.2, 1),  # light green
            15: (0.2, 0.2, 0.8, 1),  # dark blue
            16: (0.9, 0.6, 0.2, 1),  # gold
            17: (0.6, 0.0, 0.6, 1),  # purple
            18: (0.0, 0.4, 0.8, 1),  # medium blue
            19: (0.8, 0.4, 0.6, 1),  # pastel pink
        }

        # Keyboard Shortcuts (Accelerators)
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)

        # Ctrl+Q to quit
        key, mod = Gtk.accelerator_parse("<Control>q")
        self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, self._on_ctrl_q)

        # Ctrl+S to save image
        key, mod = Gtk.accelerator_parse("<Control>s")
        self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, self._on_ctrl_s)

        # Vertical Box
        outerbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(outerbox)

        # Popover for Main Menu
        popover_menu = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        bt = Gtk.ModelButton(label=f"About {self.app.name}")
        bt.connect("clicked", self._on_click_about)
        vbox.pack_start(bt, False, True, 10)
        vbox.show_all()
        popover_menu.add(vbox)
        popover_menu.set_position(Gtk.PositionType.BOTTOM)

        # Header Bar
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.props.title = self.app.name
        self.set_titlebar(headerbar)

        # Menu Button
        bt = Gtk.MenuButton(popover=popover_menu)
        icon = Gio.ThemedIcon(name=self.menu_icon)
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        bt.set_tooltip_text("Main Menu")
        bt.add(img_icon)
        headerbar.pack_end(bt)

        # Save Button
        bt = Gtk.Button()
        icon = Gio.ThemedIcon(name=self.save_icon)
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        bt.set_tooltip_text("Save Diagram")
        bt.add(img_icon)
        bt.connect("clicked", self._on_click_save)
        headerbar.pack_end(bt)

        # Edit button
        bt = Gtk.Button()
        icon = Gio.ThemedIcon(name=self.edit_icon)
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        bt.set_tooltip_text("Edit Parameters")
        bt.add(img_icon)
        bt.connect("clicked", self._on_click_edit)
        headerbar.pack_end(bt)

        # Play/Pause Button
        bt = Gtk.Button()
        icon_name = self.pause_icon if self.app.timer.is_running else self.play_icon  # set initial icon based on timer state
        icon = Gio.ThemedIcon(name=icon_name)
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        bt.set_tooltip_text("Play/Pause")
        bt.add(img_icon)
        bt.connect("clicked", self._on_click_play_pause)
        headerbar.pack_start(bt)
        self.bt_play_pause = bt  # save a reference to toggle its icon

        # Next Button
        bt = Gtk.Button()
        icon = Gio.ThemedIcon(name=self.next_icon)
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        bt.set_tooltip_text("Next")
        bt.add(img_icon)
        bt.connect("clicked", self._on_click_next)
        headerbar.pack_start(bt)

        # Skip button
        bt = Gtk.Button()
        icon = Gio.ThemedIcon(name=self.skip_icon)
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        bt.set_tooltip_text("Skip")
        bt.add(img_icon)
        bt.connect("clicked", self._on_click_skip)
        headerbar.pack_start(bt)

        # Restart button
        bt = Gtk.Button()
        icon = Gio.ThemedIcon(name=self.restart_icon)
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        bt.set_tooltip_text("Restart")
        bt.add(img_icon)
        bt.connect("clicked", self._on_click_restart)
        headerbar.pack_start(bt)

        # Speed Slider
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, min=10, max=300, step=1)
        slider.set_draw_value(False)
        slider.set_size_request(120, -1)
        slider.set_value(self.app.timer.interval_ms)
        slider.connect("value-changed", self._on_slider_value_changed)
        slider.set_tooltip_text("Change Speed")
        headerbar.pack_start(slider)

        # Stack - holds multiple "pages" (widgets) and shows one at a time
        stack = Gtk.Stack()

        # Diagram Drawing Parameters
        self.rect_length = 10                     # width of a rectangle
        self.rect_x0 = 20 + self.rect_length      # initial x
        self.rect_y0 = 20                         # initial y
        self.rect_height = 10                     # height of a task rectangle
        self.lines_dist_y = self.rect_height + 2  # vertical distance between task lines
        self.rect_offset_x = self.rect_x0         # current x position for drawing (advances with time)

        # Window initial size
        win_width = 620
        win_height = 300
        self.set_size_request(win_width, win_height)
        self.set_resizable(True)
        self.set_border_width(6)

        # Diagram Tab (Stack Page 1)
        self.drawingarea_diagram = Gtk.DrawingArea()
        self.drawingarea_diagram.connect("draw", self._on_draw_task_lines_text)  # draws task numbers
        self.drawingarea_diagram.connect("draw", self._on_draw_task_rects)       # draws the rectangles
        self.drawingarea_diagram.connect("draw", self._on_draw_info)             # draws info below the diagram
        self.drawingarea_diagram.connect("button-press-event", self._on_click_task_rect)
        self.drawingarea_diagram.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        self.update_diagram_size()  # set initial size of the drawing area

        # ScrolledWindow to allow scrolling the diagram
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.drawingarea_diagram)
        stack.add_titled(scrolled_window, "diagram", "Diagram")

        # Info Tab (Stack Page 2)
        self.label_info = Gtk.Label()
        self.refresh_info_label()  # set the label with initial data
        stack.add_titled(self.label_info, "info", "Info")

        # Task Popover when clicking on  a task rectangle
        self.popover_task = Gtk.Popover()
        self.label_task = Gtk.Label()
        self.popover_task.add(self.label_task)

        # State attributes for managing popover clicks
        self.is_popover_task_active = False
        self.cursor_x_at_popover = None
        self.cursor_y_at_popover = None

        # Connect a click event to the whole window to detect clicks outside the popover
        self.connect("button-press-event", self._on_click_outside_popover)

        # Stack Switcher - creates the tab buttons to switch the stack
        stackswitcher = Gtk.StackSwitcher()
        stackswitcher.set_stack(stack)
        stackswitcher.set_halign(Gtk.Align.CENTER)  # center the buttons

        # Add the stack switcher and the stack itself to the main window box
        outerbox.pack_start(stackswitcher, False, True, 0)
        outerbox.pack_start(stack, True, True, 0)

    def _on_ctrl_q(self, accel_group, window, key, modifier):
        self.app.quit()

    def _on_ctrl_s(self, accel_group, window, key, modifier):
        self._open_save_dialog()

    def _on_click_save(self, widget):
        self._open_save_dialog()

    def _open_save_dialog(self):
        dialog = Gtk.FileChooserDialog(title="Save Diagram", parent=self, action=Gtk.FileChooserAction.SAVE)
        dialog.set_do_overwrite_confirmation(True)
        dialog.set_current_folder(os.path.expanduser("~"))  # start in home dir
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
        file_filter.set_name("PNG Images")
        file_filter.add_mime_type("image/png")
        dialog.add_filter(file_filter)

        file_filter = Gtk.FileFilter()
        file_filter.set_name("All Files")
        file_filter.add_pattern("*")
        dialog.add_filter(file_filter)

    def update_diagram_size(self):
        # Recalculates and sets the size of the drawing area based on task data
        drawingarea_width = sum(task.duration for task in self.list_tasks) * self.rect_length * 1.05
        drawingarea_height = len(self.list_tasks) * self.lines_dist_y * 1.1

        self.drawingarea_diagram.set_size_request(drawingarea_width, drawingarea_height)

    def set_play_icon_on_finish(self):
        # Called when the simulation ends to force the Play/Pause button to show the Play icon
        self.app.timer.stop()
        button = self.bt_play_pause

        # Remove the current icon
        bt_child = button.get_child()
        if bt_child:
            button.remove(bt_child)

        # Add the Play icon
        icon_name = self.play_icon
        icon = Gio.ThemedIcon(name=icon_name)
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(img_icon)
        button.show_all()

    def _on_slider_value_changed(self, scale):
        self.app.timer.change_interval_ms(scale.get_value())
        self.refresh_info_label()
        self.drawingarea_diagram.queue_draw()  # redraw to update info text

    def _on_click_play_pause(self, button):
        bt_child = button.get_child()
        if bt_child:
            button.remove(bt_child)

        # Toggle the timer and determine the new icon
        if self.app.timer.is_running:
            icon_name = self.play_icon
            self.app.timer.stop()
        elif self.app.scheduler.has_tasks():
            icon_name = self.pause_icon
            self.app.timer.start()
        else:
            # No tasks left, keep Play icon
            icon_name = self.play_icon
            self.app.timer.stop()

        # Add the new icon
        icon = Gio.ThemedIcon(name=icon_name)
        img_icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(img_icon)
        button.show_all()

    def _on_click_next(self, button):
        self.app.tick()

    def _on_click_skip(self, button):
        self.app.skip()

    def _on_click_restart(self, widget):
        self._restart_rects()
        self.update_diagram_size()
        self.refresh_info_label()

    def _restart_rects(self):
        # Resets the diagram and simulation state
        self.list_task_rects = [] # clear all drawn rectangles
        self.rect_offset_x = self.rect_x0  # reset drawing position
        self.drawingarea_diagram.queue_draw() # redraw the empty diagram

        self.app.scheduler.reset()
        self.list_tasks = self.app.scheduler.list_tasks

    def _on_click_edit(self, widget):
        self.app.scheduler.edit_file()


    def _on_click_outside_popover(self, widget, event):
        # Hides the task popover if a click occurs anywhere else on the window
        if (self.is_popover_task_active == True and
            event.x != self.cursor_x_at_popover and
            event.y != self.cursor_y_at_popover):
            self.is_popover_task_active = False
            self.popover_task.hide()

    def _on_click_task_rect(self, widget, event):
        # Check if the click was on a task rectangle
        if (event.type == Gdk.EventType.BUTTON_PRESS and
            event.button == Gdk.BUTTON_PRIMARY):
            for rect in self.list_task_rects:
                if (rect.x <= event.x <= rect.x + rect.width and
                    rect.y <= event.y <= rect.y + rect.height):
                    self._show_task_popover(rect, widget, event)
                    break  # stop after finding the first match

    def _on_click_about(self, widget):
        about = Gtk.AboutDialog(transient_for=self, modal=True)
        about.set_program_name(self.app.name)
        about.set_version(self.app.version)
        about.set_comments(self.app.description)
        about.set_website(self.app.website_url)
        about.set_website_label(self.app.website_label)
        about.set_authors(self.app.authors)
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_copyright(self.app.copyright)

        if self.pixbuf:
            about.set_logo(self.pixbuf)

        about.connect("response", lambda dialog, response: dialog.destroy())
        about.present()

    def _on_draw_task_lines_text(self, widget, cr: cairo.Context):
        # Draws the task id numbers on the left side
        
        cr.set_source_rgb(0.7, 0.7, 0.7)
        cr.set_font_size(10)
        
        for task_num, _ in enumerate(self.list_tasks, 1):
            y_pos = self.rect_y0 + self.lines_dist_y * (task_num - 1) + self.rect_height - 2
            x_pos = 0 if task_num >= 10 else self.rect_x0 / 4

            # Draw the text
            cr.move_to(x_pos, y_pos)
            cr.show_text(str(task_num))

    def _on_draw_task_rects(self, widget, cr: cairo.Context):
        for rect in self.list_task_rects:
            cr.set_source_rgba(*rect.color)
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.fill()

    def _on_draw_info(self, widget, cr: cairo.Context):
        # Draws the statistics below the diagram

        cr.set_source_rgb(0.7, 0.7, 0.7)
        cr.set_font_size(10)

        # Starting position
        y = self.rect_y0 + self.lines_dist_y * len(self.list_tasks) + 30
        x_offset = self.rect_x0
        spacing = 20

        # Statistics to display
        texts = [
            f"Algorithm: {self.app.scheduler.alg_scheduling}",
            f"Total tasks: {len(self.list_tasks)}",
            f"Terminated tasks: {self.app.scheduler.num_term_tasks}",
            f"CLK period: {self.app.timer.interval_ms:.0f} ms",
            f"Quantum: {self.app.scheduler.quantum}",
            f"Turnaround time: {sum(t.turnaround_time for t in self.list_tasks) / len(self.list_tasks)}",
            f"Average waiting time: {sum(t.waiting_time for t in self.list_tasks) / len(self.list_tasks)}",
            f"Time: {self.app.scheduler.time}",
        ]

        # Draw each piece of text, advancing horizontally
        for text in texts:
            cr.move_to(x_offset, y)
            cr.show_text(text)

            # Measure text to calculate position for the next item
            extents = cr.text_extents(text)
            x_offset += (extents.width + spacing)

    def _show_task_popover(self, rect, widget, event):
        self.label_task.set_markup(f"<b>task id:</b> {rect.task_record.task.id}\n"
                                   f"<b>start time:</b> {rect.task_record.task.start_time}\n"
                                   f"<b>duration:</b> {rect.task_record.task.duration}\n"
                                   f"<b>priority:</b> {rect.task_record.task.priority}\n"
                                   f"<b>progress:</b> {rect.task_record.progress}\n"
                                   f"<b>state:</b> {rect.task_record.state}\n"
                                   f"<b>turnaround time:</b> {rect.task_record.turnaround_time}\n"
                                   f"<b>waiting time:</b> {rect.task_record.waiting_time}\n"
                                   f"<b>time:</b> {rect.task_record.time}"
        )
        
        # Store click coordinates to help hiding the popover
        self.cursor_x_at_popover = event.x
        self.cursor_y_at_popover = event.y
        self.is_popover_task_active = True
        
        # Set popover position relative to the clicked rectangle
        self.popover_task.set_relative_to(widget)
        self.popover_task.set_pointing_to(rect)
        self.popover_task.set_position(Gtk.PositionType.TOP)
        self.popover_task.show_all()

    def refresh_info_label(self):
        # Updates the text on the Info tab
        self.label_info.set_markup(
            f"<big><b>Algorithm:</b> {self.app.scheduler.alg_scheduling}</big>\n"
            f"<big><b>Total tasks:</b> {len(self.list_tasks)}</big>\n"
            f"<big><b>Terminated tasks:</b> {self.app.scheduler.num_term_tasks}</big>\n"
            f"<big><b>CLK period:</b> {self.app.timer.interval_ms:.0f} ms</big>\n"
            f"<big><b>Quantum:</b> {self.app.scheduler.quantum}</big>\n"
            f"<big><b>Turnaround time:</b> {sum(t.turnaround_time for t in self.list_tasks) / len(self.list_tasks)}</big>\n"
            f"<big><b>Average waiting time:</b> {sum(t.waiting_time for t in self.list_tasks) / len(self.list_tasks)}</big>\n"
            f"<big><b>Time:</b> {self.app.scheduler.time}</big>"
        )

    def draw_new_rect(self, current_task):
        # Create semi-transparent grey task rectangles
        for task in self.list_tasks:
            if (task != current_task and
                task.start_time < self.app.scheduler.time and
                task.state == "ready"):
                self.list_task_rects.append(TaskRectangle(
                    self.rect_offset_x - self.rect_length,
                    self.rect_y0 + self.lines_dist_y*(task.id-1),
                    self.rect_length,
                    self.rect_height,
                    (0.5, 0.5, 0.5, 0.5),
                    TaskRecord(task, task.state, task.progress, task.turnaround_time, task.waiting_time, self.app.scheduler.time)
                ))

        # Create the colored rectangle for the currently executing task
        if current_task:
            self.list_task_rects.append(TaskRectangle(
                self.rect_offset_x - self.rect_length,
                self.rect_y0 + self.lines_dist_y*(current_task.id-1),
                self.rect_length,
                self.rect_height,
                self.dict_colors[current_task.color_num],
                TaskRecord(current_task, current_task.state, current_task.progress, current_task.turnaround_time, current_task.waiting_time, self.app.scheduler.time) # data
            ))

        # Advance the horizontal drawing position for the next tick
        self.rect_offset_x += (self.rect_length + 1)

        # Draw
        self.drawingarea_diagram.queue_draw()

    def _save_diagram_to_png(self, filename):
        # Calculate the bounds of the diagram
        max_x = max(rect.x + rect.width  for rect in self.list_task_rects) if self.list_task_rects else 100
        max_y = max(rect.y + rect.height for rect in self.list_task_rects) if self.list_task_rects else 100

        # Add padding
        surface_width  = int(max_x + self.rect_x0)
        surface_height = int(max_y + self.rect_y0)

        # Create Cairo surface
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, surface_width, surface_height)
        cr = cairo.Context(surface)

        # Set a white background
        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        # Draw all the rectangles onto the surface
        for rect in self.list_task_rects:
            cr.set_source_rgba(*rect.color)
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.fill()

        # Write the surface to a PNG file
        try:
            surface.write_to_png(filename)
            surface.finish()
        except Exception as e:
            print(f"Failed to save diagram image at {filename}: {e}")
