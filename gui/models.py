from tkinter import font

import settings
from factory import *


class PikaxGuiComponent:

    def __init__(self, master, pikax_handler):
        self.master = master
        self._frame = Frame(master)
        self._frame.configure(borderwidth=0, highlightthickness=0)
        self._pikax_handler = pikax_handler
        self._width = settings.MAIN_WINDOW_WIDTH
        self._height = settings.MAIN_WINDOW_HEIGHT
        self._label_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE,
                                     weight=font.BOLD)
        self._entry_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 2)
        self._button_font = self.entry_font
        # subclass must set these
        self._grid_height = -1
        self._grid_width = -1
        self.is_grid_width_set = False
        self.is_grid_height_set = False

    def destroy(self):
        raise NotImplementedError

    @property
    def grid_width(self):
        if not self.is_grid_width_set:
            raise ValueError('grid width is not set')
        return self._grid_width

    @grid_width.setter
    def grid_width(self, value):
        self._grid_width = value
        self.is_grid_width_set = True

    @property
    def grid_height(self):
        if not self.is_grid_height_set:
            raise ValueError('grid height is not set')
        return self._grid_height

    @grid_height.setter
    def grid_height(self, value):
        self._grid_height = value
        self.is_grid_height_set = True

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def frame(self):
        return self._frame

    @property
    def label_font(self):
        return self._label_font

    @property
    def button_font(self):
        return self._button_font

    @property
    def entry_font(self):
        return self._entry_font

    @property
    def pikax_handler(self):
        return self._pikax_handler

    def make_button(self, text=''):
        return make_button(self.frame, text=text)

    def make_label(self, text=''):
        return make_label(self.frame, text=text)

    def make_frame(self):
        return make_frame(self.frame)

    def make_dropdown(self, default, choices):
        return make_dropdown(self.frame, default, choices)

    def make_entry(self):
        return make_entry(self.frame)

    def make_download_output(self):
        text = make_text(self.frame)
        text.configure(height=6, state=DISABLED)
        return text


    @staticmethod
    def grid(component, row=None, column=None, rowspan=None, columnspan=None):
        if row:
            component.grid_configure(row=int(row))
        if column:
            component.grid_configure(column=int(column))
        if rowspan:
            component.grid_configure(rowspan=int(rowspan))
        if columnspan:
            component.grid_configure(columnspan=int(columnspan))
        component.grid()

    @staticmethod
    def pack(component):
        component.pack()

    def make_fullscreen_canvas(self):
        return Canvas(self.frame, borderwidth=0, highlightthickness=0,
                      height=self.height, width=self.width)

    @staticmethod
    def redirect_output_to(text_component, text_widget=True, canvas=None):
        import sys
        if text_widget:
            from common import StdoutTextWidgetRedirector
            sys.stdout = StdoutTextWidgetRedirector(text_component)
        else:
            from common import StdoutCanvasTextRedirector
            sys.stdout = StdoutCanvasTextRedirector(canvas, text_component)


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

    def add_text(self, canvas, text, row=0, column=0, rowspan=1, columnspan=1, font=None, color='black'):

        width, height = self.get_canvas_location(row, column, rowspan, columnspan)

        if not font:
            font = self.label_font

        return canvas.create_text((width, height), text=text, font=font, fill=color)

    def add_widget(self, canvas, widget, row=0, column=0, rowspan=1, columnspan=1):
        width, height = self.get_canvas_location(row=row, column=column, rowspan=rowspan, columnspan=columnspan)
        return canvas.create_window((width, height), window=widget)
