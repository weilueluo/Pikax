import tkinter as tk
import webbrowser
from tkinter import font

from PIL import Image, ImageTk

import settings
from common import crop_to_dimension, get_background_file_path


class PikaxOptionMenu(tk.OptionMenu):

    def __init__(self, master, default, *args, **kwargs):
        self.var = tk.StringVar(master)
        self.var.set(default)
        super().__init__(master, self.var, *args, **kwargs)

    def get(self):
        return self.var.get().strip()


class PikaxGuiComponent:

    def __init__(self, master, pikax_handler):
        self.master = master
        self.frame = self.make_frame(borderwidth=0, highlightthickness=0)
        self.pikax_handler = pikax_handler
        self.width = settings.MAIN_WINDOW_WIDTH
        self.height = settings.MAIN_WINDOW_HEIGHT

        #
        # settings
        #

        # texts
        self.issue_text = 'Report'
        self.title_text = settings.TITLE + ' ' + settings.VERSION

        # fonts
        self.text_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE,
                                   weight=font.BOLD)
        self.entry_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 2)
        self.button_font = self.entry_font
        self.dropdown_font = self.entry_font
        self.output_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 4)
        self.canvas_artist_font = font.Font(family='Courier', size=10)

        # text colors
        self.title_color = '#51abc2'
        self.display_text_color = '#51abc2'
        self.input_text_color = 'white'
        self.artist_name_color = '#1b5361'
        # button colors
        self.button_color = '#1b5361'
        self.entry_color = '#1b5361'
        self.pressed_button_color = '#0c313b'
        self.cursor_color = 'white'

        self.grid_height = self.height
        self.grid_width = self.width

        # sizes
        self.button_width = 10
        self.title_font_size = 12
        self.dropdown_width = 16

        #
        # default operations
        #

        # add canvas background
        self.canvas = self.set_canvas(image_path=get_background_file_path(), focus=tk.CENTER)

        # add title
        title_font = font.Font(family='Arial', size=self.title_font_size, weight=font.BOLD)
        self.canvas_title = self.add_text(text=self.title_text, font=title_font, row=20, column=60, columnspan=2,
                                          color=self.title_color)
        # add issue button
        self.issue_button = self.make_button(text=self.issue_text)
        self.issue_button_id = self.add_widget(widget=self.issue_button, row=self.grid_height - 30,
                                               column=self.grid_width - 75)
        self.issue_button.configure(command=self.issue_button_pressed)
        # add background artist reference
        self.artist_reference = self.add_text(text=f'*background by {settings.CANVAS_BACKGROUND_ARTIST_NAME}',
                                              row=self.grid_height - 26, column=100,
                                              columnspan=2, font=self.canvas_artist_font,
                                              color=self.artist_name_color)

    def destroy(self):
        self.frame.destroy()

    def set_canvas(self, image_path, focus):
        im = crop_to_dimension(Image.open(image_path), focus=focus, width_ratio=self.width, height_ratio=self.height)
        im = im.resize((self.width, self.height))
        im = ImageTk.PhotoImage(image=im)
        background = self.make_fullscreen_canvas()
        background.create_image((0, 0), image=im, anchor=tk.NW)
        background.image = im  # keep a reference prevent gc-ed
        self.grid(background, row=0, column=0, rowspan=self.grid_height, columnspan=self.grid_width)
        return background

    def make_download_output(self, *args, **kwargs):
        text = self.make_text(*args, **kwargs)
        text.configure(height=6, width=58)
        return text

    @staticmethod
    def grid(component, row=None, column=None, rowspan=None, columnspan=None, *args, **kwargs):
        if row:
            component.grid_configure(row=int(row))
        if column:
            component.grid_configure(column=int(column))
        if rowspan:
            component.grid_configure(rowspan=int(rowspan))
        if columnspan:
            component.grid_configure(columnspan=int(columnspan))
        component.grid(*args, **kwargs)

    @staticmethod
    def pack(component, *args, **kwargs):
        component.pack(*args, **kwargs)

    def make_fullscreen_canvas(self):
        return tk.Canvas(self.frame, borderwidth=0, highlightthickness=0,
                         height=self.height, width=self.width)

    def redirect_output_to(self, text_component, text_widget=True):
        import sys
        if text_widget:
            from common import StdoutTextWidgetRedirector
            sys.stdout = StdoutTextWidgetRedirector(text_component)
        else:
            from common import StdoutCanvasTextRedirector
            sys.stdout = StdoutCanvasTextRedirector(self.canvas, text_component)

    def get_canvas_location(self, row, column, rowspan, columnspan):
        if row < 0 or row > self.grid_height:
            raise ValueError(f'Invalid row: {row}, expected: 0 <= row <= {self.grid_height}')
        if column < 0 or column > self.grid_width:
            raise ValueError(f'Invalid column: {column}, expected: 0 <= column <= {self.grid_width}')
        if row + rowspan < 0 or row + rowspan > self.grid_height:
            raise ValueError(f'Invalid rowspan: {rowspan}, expected: 0 <= {row} + rowspan <= {self.grid_height}')
        if column + columnspan < 0 or column + columnspan > self.grid_width:
            raise ValueError(
                f'Invalid columnspan: {columnspan}, expected: 0 <= {column} + columnspan <= {self.grid_width}')

        row_height = self.height / self.grid_height
        column_width = self.width / self.grid_width

        row_start = row_height * row
        row_end = row_height * (row + rowspan)
        height = (row_end + row_start) / 2

        column_start = column_width * column
        column_end = column_width * (column + columnspan)
        width = (column_start + column_end) / 2

        return width, height

    def add_text(self, text, row=0, column=0, rowspan=1, columnspan=1, font=None, color=None):

        width, height = self.get_canvas_location(row, column, rowspan, columnspan)

        if not font:
            font = self.text_font
        if not color:
            color = self.display_text_color
        return self.canvas.create_text((width, height), text=text, font=font, fill=color)

    def add_widget(self, widget, row=0, column=0, rowspan=1, columnspan=1):
        width, height = self.get_canvas_location(row=row, column=column, rowspan=rowspan, columnspan=columnspan)
        return self.canvas.create_window((width, height), window=widget)

    @staticmethod
    def issue_button_pressed():
        webbrowser.open(settings.ISSUE_URL)

    def make_button(self, *args, **kwargs):
        return tk.Button(master=self.frame,
                         relief=tk.FLAT,
                         padx=10,
                         pady=2,
                         borderwidth=0,
                         highlightthickness=0,
                         activebackground=self.pressed_button_color,
                         bg=self.button_color,
                         fg=self.display_text_color,
                         width=self.button_width,
                         font=self.button_font,
                         *args,
                         **kwargs
                         )

    def make_label(self, *args, **kwargs):
        return tk.Label(master=self.frame, *args, **kwargs)

    def make_frame(self, *args, **kwargs):
        return tk.Frame(master=self.master, *args, **kwargs)

    def make_dropdown(self, default, choices, **kwargs):
        dropdown_len = 30
        for index, choice in enumerate(choices):
            spaces_left = dropdown_len - len(choice) / 2
            if spaces_left > 0:
                choices[index] = (' ' * int(spaces_left / 2)) + choice + (' ' * int(spaces_left / 2))

        dropdown = PikaxOptionMenu(self.frame, default, *choices)
        dropdown.configure(
            width=self.dropdown_width,
            bg=self.entry_color,
            fg=self.input_text_color,
            font=self.dropdown_font,
            activebackground=self.pressed_button_color,
            borderwidth=0,
            highlightthickness=0,
            **kwargs
        )
        return dropdown

    def make_entry(self, *args, **kwargs):
        return tk.Entry(
            master=self.frame,
            borderwidth=0,
            highlightthickness=0,
            justify=tk.CENTER,
            bg=self.entry_color,
            fg=self.input_text_color,
            insertbackground=self.cursor_color,
            font=self.entry_font,
            *args,
            **kwargs
        )

    def make_text(self, *args, **kwargs):
        return tk.Text(
            master=self.frame,
            wrap=tk.WORD,
            height=1,
            width=80,
            state=tk.NORMAL,
            highlightthickness=0,
            borderwidth=0,
            bg=self.entry_color,
            fg=self.input_text_color,
            *args,
            **kwargs
        )
