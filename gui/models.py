import tkinter as tk
import webbrowser
from tkinter import font, ttk

from PIL import Image, ImageTk

import settings
import texts
from common import crop_to_dimension, get_background_file_path


class PikaxOptionMenu(tk.OptionMenu):

    def __init__(self, master, default, *args, **kwargs):
        self.var = tk.StringVar(master)
        self.var.set(default)
        super().__init__(master, self.var, *args, **kwargs)

    def get(self):
        return self.var.get().strip()


class PikaxCheckButton(tk.Button):
    def __init__(self, master, initial=False, text='', *args, **kwargs):
        self.checked = initial
        self.text = text
        super().__init__(master=master, command=self.clicked, *args, **kwargs)
        self.set(value=self.checked)

    def set(self, value=False):
        self.checked = value
        text = texts.TICK + ' ' + self.text if self.checked else texts.CROSS + ' ' + self.text
        self.configure(text=text)

    def clicked(self, event=None):
        self.set(value=not self.checked)

    def get(self):
        return self.checked


class PikaxSwitchButton(tk.Button):
    def __init__(self, master, values, default=None, *args, **kwargs):
        if default is None:
            default = values[0]

        self.values = values
        self.curr_value = default
        self.curr_index = values.index(self.curr_value)
        super().__init__(master=master, text=str(self.curr_value), command=self.clicked, *args, **kwargs)

    def get_next_value(self):
        self.curr_index = (self.curr_index + 1) % len(self.values)
        return self.values[self.curr_index]

    def get(self):
        return self.values[self.curr_index]

    def clicked(self, event=None):
        self.configure(text=str(self.get_next_value()))


class PikaxGuiComponent:

    def __init__(self, master, pikax_handler):
        self.master = master
        self.frame = self.make_frame(borderwidth=0, highlightthickness=0)
        self.pikax_handler = pikax_handler
        # this is important when opening another window, else winfo width & height will return 1
        self.master.update()
        self.width = self.master.winfo_width()
        self.height = self.master.winfo_height()

        #
        # settings
        #

        # texts
        self.issue_text = texts.MODELS_ISSUE_TEXT
        self.title_text = texts.TITLE_TEXT

        # fonts
        self.text_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE,
                                   weight=font.BOLD)
        self.input_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 2)
        self.button_font = self.input_font
        self.dropdown_font = self.input_font
        self.output_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 4)
        self.canvas_artist_font = font.Font(family='Courier', size=10)

        # text colors
        self.title_color = '#51abc2'
        self.display_text_color = '#51abc2'
        self.input_text_color = 'white'
        self.artist_name_color = '#1b5361'

        # button colors
        self.button_color = '#1b5361'
        self.input_color = '#1b5361'
        self.active_input_color = '#0c313b'
        self.cursor_color = 'white'
        self.checkbox_text_and_tick_color = '#c7a12e'

        self.grid_height = self.height
        self.grid_width = self.width

        # sizes
        self.button_width = 10
        self.title_font_size = 12
        self.dropdown_width = 18
        self.switch_button_width = 18
        self.button_padx = 10
        self.button_pady = 2
        self.text_padx = 10
        self.text_pady = 10

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
        self.artist_reference = self.add_text(
            text=texts.MODELS_ARTIST_REFERENCE_TEXT.format(artist_name=settings.CANVAS_BACKGROUND_ARTIST_NAME),
            row=self.grid_height - 26, column=100,
            columnspan=2, font=self.canvas_artist_font,
            color=self.artist_name_color)

        # set combobox style
        combo_style = ttk.Style()
        combo_style_name = 'combo_style'
        if combo_style_name not in combo_style.theme_names():
            combo_style.theme_create(combo_style_name, parent='classic',
                                     settings={'TCombobox': {'configure': {
                                         'selectbackground': self.input_color,
                                         'fieldbackground': self.input_color,
                                         'background': self.input_color,
                                         'foreground': self.input_text_color,
                                         'borderwidth': 0,
                                         'highlightthickness': 0,
                                         'width': self.dropdown_width,
                                         'justify': tk.CENTER
                                     }}},
                                     )
            # ATTENTION: this applies the new style 'combo_style' to all ttk.Combobox
            combo_style.theme_use(combo_style_name)
            self.master.option_add('*TCombobox*Listbox.background', self.input_color)
            self.master.option_add('*TCombobox*Listbox.foreground', self.input_text_color)

    def destroy(self):
        self.frame.destroy()

    def get_cropped_image(self, image_path, focus=tk.CENTER):
        im = crop_to_dimension(Image.open(image_path), focus=focus, width_ratio=self.width, height_ratio=self.height)
        im = im.resize((self.width, self.height))
        im = ImageTk.PhotoImage(image=im)
        return im

    def set_canvas(self, image_path, focus):
        im = self.get_cropped_image(image_path=image_path, focus=focus)
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

    def redirect_output_to(self, text_component, text_widget=True, canvas=None):
        import sys
        if text_widget:
            from common import StdoutTextWidgetRedirector
            sys.stdout = StdoutTextWidgetRedirector(text_component)
        else:
            from common import StdoutCanvasTextRedirector
            if not canvas:
                canvas = self.canvas
            sys.stdout = StdoutCanvasTextRedirector(canvas, text_component)

    def get_canvas_location(self, row, column, rowspan, columnspan):
        if row < 0 or row > self.grid_height:
            raise ValueError(texts.MODELS_INVALID_ROW_ERROR.format(row=row, grid_height=self.grid_height))
        if column < 0 or column > self.grid_width:
            raise ValueError(texts.MODELS_INVALID_COLUMN_ERROR.format(column=column, grid_width=self.grid_width))
        if row + rowspan < 0 or row + rowspan > self.grid_height:
            raise ValueError(
                texts.MODELS_INVALID_ROWSPAN_ERROR.format(rowspan=rowspan, row=row, grid_height=self.grid_height))
        if column + columnspan < 0 or column + columnspan > self.grid_width:
            raise ValueError(texts.MODELS_INVALID_COLUMNSPAN_ERROR.format(columnspan=columnspan, column=column,
                                                                          grid_width=self.grid_width))

        row_height = self.height / self.grid_height
        column_width = self.width / self.grid_width

        row_start = row_height * row
        row_end = row_height * (row + rowspan)
        height = (row_end + row_start) / 2

        column_start = column_width * column
        column_end = column_width * (column + columnspan)
        width = (column_start + column_end) / 2

        return width, height

    def add_text(self, text, row=0, column=0, rowspan=1, columnspan=1, font=None, color=None, canvas=None):

        width, height = self.get_canvas_location(row, column, rowspan, columnspan)

        if not font:
            font = self.text_font
        if not color:
            color = self.display_text_color
        if not canvas:
            canvas = self.canvas
        return canvas.create_text((width, height), text=text, font=font, fill=color, justify=tk.CENTER)

    def add_widget(self, widget, row=0, column=0, rowspan=1, columnspan=1):
        width, height = self.get_canvas_location(row=row, column=column, rowspan=rowspan, columnspan=columnspan)
        return self.canvas.create_window((width, height), window=widget)

    @staticmethod
    def issue_button_pressed():
        webbrowser.open(settings.ISSUE_URL)

    def make_button(self, *args, **kwargs):
        return tk.Button(master=self.frame,
                         relief=tk.FLAT,
                         padx=self.button_padx,
                         pady=self.button_pady,
                         borderwidth=0,
                         highlightthickness=0,
                         activebackground=self.active_input_color,
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
        dropdown = ttk.Combobox(self.frame, values=choices)
        dropdown.set(default)
        dropdown.configure(
            width=self.dropdown_width,
            font=self.dropdown_font,
            state='readonly',
            justify=tk.CENTER,
            **kwargs
        )
        dropdown.option_add('*TCombobox*Listbox.Justify', 'center')
        return dropdown

    def make_entry(self, justify=tk.CENTER, *args, **kwargs):
        return tk.Entry(
            master=self.frame,
            borderwidth=0,
            highlightthickness=0,
            justify=justify,
            bg=self.input_color,
            fg=self.input_text_color,
            insertbackground=self.cursor_color,
            font=self.input_font,
            *args,
            **kwargs
        )

    def make_text(self, wrap=tk.WORD, height=1, width=80, state=tk.NORMAL, *args, **kwargs):
        text = tk.Text(
            master=self.frame,
            wrap=wrap,
            height=height,
            width=width,
            state=state,
            highlightthickness=0,
            borderwidth=0,
            bg=self.input_color,
            fg=self.input_text_color,
            font=self.output_font,
            insertbackground=self.cursor_color,
            padx=self.text_padx,
            pady=self.text_pady,
            *args,
            **kwargs
        )
        return text

    def make_checkbutton(self, initial=False, *args, **kwargs):
        return PikaxCheckButton(master=self.frame,
                                initial=initial,
                                bg=self.input_color,
                                fg=self.display_text_color,
                                activebackground=self.active_input_color,
                                padx=self.button_padx,
                                pady=self.button_pady,
                                highlightthickness=0,
                                borderwidth=0,
                                *args, **kwargs)

    def make_switchbutton(self, values, default=None, *args, **kwargs):
        return PikaxSwitchButton(
            master=self.frame,
            values=values,
            default=default,
            bg=self.input_color,
            fg=self.display_text_color,
            padx=self.button_padx,
            pady=self.button_pady,
            activebackground=self.active_input_color,
            highlightthickness=0,
            borderwidth=0,
            font=self.dropdown_font,
            width=self.switch_button_width,
            *args,
            **kwargs
        )
