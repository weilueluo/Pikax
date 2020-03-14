import tkinter as tk
import webbrowser
from tkinter import font, ttk

from PIL import Image, ImageTk

import settings
import texts
from common import crop_to_dimension, get_background_file_path, refresh, save_language, open_image, get_tk_image


class PikaxButton(tk.Button):
    bg_color = '#1b5361'
    fg_color = '#51abc2'
    bg_hover_color = '#186b73'
    fg_hover_color = '#2eccdb'
    active_color = '#0c313b'
    width = 10
    padx = 10
    pady = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 2)

        self.configure(relief=tk.FLAT,
                       padx=self.padx,
                       pady=self.pady,
                       borderwidth=0,
                       highlightthickness=0,
                       activebackground=self.active_color,
                       bg=self.bg_color,
                       fg=self.fg_color,
                       width=self.width,
                       font=self.font
                       )

        self.bind('<Enter>', self.mouse_enter)
        self.bind('<Leave>', self.mouse_leave)

    def mouse_enter(self, _=None):
        if self['state'] != tk.DISABLED:
            self.configure(bg=self.bg_hover_color, fg=self.fg_hover_color)

    def mouse_leave(self, _=None):
        self.configure(bg=self.bg_color, fg=self.fg_color)


class PikaxOptionMenu(tk.OptionMenu):

    def __init__(self, master, default, *args, **kwargs):
        self.var = tk.StringVar(master)
        self.var.set(default)
        super().__init__(master, self.var, *args, **kwargs)

    def get(self):
        return self.var.get().strip()


class PikaxCheckButton(PikaxButton):
    padx = 20

    def __init__(self, master, initial=False, text='', *args, **kwargs):
        super().__init__(master=master, command=self.clicked, *args, **kwargs)
        self.font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 4)
        self.checked = initial
        self.text = text
        self.set(value=self.checked)

        self.configure(font=self.font, padx=self.padx)

    def set(self, value=False):
        self.checked = value
        text = texts.get('TICK') + ' ' + self.text if self.checked else texts.get('CROSS') + ' ' + self.text
        self.configure(text=text)

    def clicked(self, _=None):
        self.set(value=not self.checked)

    def get(self):
        return self.checked


class PikaxSwitchButton(PikaxButton):
    width = 18

    def __init__(self, master, values, default=None, *args, **kwargs):
        if default is None:
            default = values[0]

        self.values = values
        try:
            self.curr_index = values.index(default)
        except ValueError:  # default not in values
            self.curr_index = 0
            default = values[0]
        super().__init__(master=master, text=str(default), command=self.clicked, *args, **kwargs)

        if 'width' in kwargs:
            self.width = kwargs['width']
        else:
            self.width = PikaxSwitchButton.width

        self.configure(width=self.width)

    def get_next_value(self):
        self.curr_index = (self.curr_index + 1) % len(self.values)
        return self.values[self.curr_index]

    def get(self):
        return self.values[self.curr_index]

    def set(self, value):
        if value not in self.values:
            raise AttributeError(
                texts.get('MODELS_SWITCHBUTTON_INVALID_SET_VALUE').format(value=value, values=self.values))
        self.curr_index = self.values.index(value)
        self.configure(text=value)

    def clicked(self, _=None):
        self.configure(text=str(self.get_next_value()))


class PikaxEntry(tk.Entry):
    bg_color = '#1b5361'
    fg_color = 'white'
    select_bg_color = '#3b818c'
    cursor_color = 'white'

    def __init__(self, master, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.justify = tk.CENTER
        self.font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 2)

        self.configure(
            borderwidth=0,
            highlightthickness=0,
            justify=self.justify,
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground=self.cursor_color,
            selectbackground=self.select_bg_color,
            font=self.font
        )


class PikaxText(tk.Text):
    wrap = tk.WORD
    height = 1
    width = 80
    padx = 10
    pady = 10
    bg_color = '#1b5361'
    fg_color = 'white'
    cursor_color = 'white'
    select_bg_color = '#3b818c'

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 4)
        self.state = tk.NORMAL

        self.configure(
            borderwidth=0,
            highlightthickness=0,
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground=self.cursor_color,
            selectbackground=self.select_bg_color,
            font=self.font,
            wrap=self.wrap,
            padx=self.padx,
            pady=self.pady
        )


dropdown_counter = 0


class PikaxDropdown(ttk.Combobox):
    bg_color = '#1b5361'
    fg_color = 'white'
    bg_hover_color = '#186b73'
    fg_hover_color = '#2eccdb'
    width = 18

    def __init__(self, master, default, choices, **kwargs):
        global dropdown_counter
        self.combo_style = ttk.Style()
        self.combo_style_name = f'custom{dropdown_counter}.TCombobox'
        dropdown_counter += 1

        super().__init__(master=master, values=choices, style=self.combo_style_name)
        self.set_style()

        self.font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 2)
        self.set(default)
        self.configure(
            width=self.width,
            font=self.font,
            state='readonly',
            justify=tk.CENTER,
            **kwargs
        )
        self.option_add('*TCombobox*Listbox.Justify', 'center')
        self.bind('<Enter>', lambda _: self.hover_enter())
        self.bind('<Leave>', lambda _: self.hover_leave())

    def hover_enter(self):
        self.combo_style.map(self.combo_style_name,
                             background=[('readonly', self.bg_hover_color)],
                             selectbackground=[('readonly', self.bg_hover_color)],
                             fieldbackground=[('readonly', self.bg_hover_color)],
                             )

    def hover_leave(self):
        self.combo_style.map(self.combo_style_name,
                             background=[('readonly', self.bg_color)],
                             selectbackground=[('readonly', self.bg_color)],
                             fieldbackground=[('readonly', self.bg_color)],
                             )

    def set_style(self):
        self.combo_style.theme_use('classic')
        self.combo_style.map(self.combo_style_name,
                             selectbackground=[('readonly', self.bg_color)],
                             selectforeground=[('readonly', self.fg_color)],
                             selectborderwidth=[('readonly', 0)],
                             fieldbackground=[('readonly', self.bg_color)],
                             foreground=[('readonly', self.fg_color)],
                             background=[('readonly', self.bg_color)],
                             arrowcolor=[('readonly', self.bg_color)],
                             borderwidth=[('readonly', 0)],
                             highlightthickness=[('readonly', 0)],
                             width=[('readonly', self.width)],
                             justify=[('readonly', tk.CENTER)],
                             )
        self.master.option_add('*TCombobox*Listbox.background', self.bg_color)
        self.master.option_add('*TCombobox*Listbox.foreground', self.fg_color)
        self.configure(state='readonly')


class PikaxGuiComponent:

    def __init__(self, master, pikax_handler):
        self.master = master
        self.frame = self.make_frame(borderwidth=0, highlightthickness=0)
        if 'frames' not in master.__dict__:
            master.frames = dict()
        master.frames[self.__class__.__name__] = self.frame
        self.pikax_handler = pikax_handler
        # this update is important when opening another different window, else winfo width & height will return 1
        self.master.update()

        #
        # settings
        #

        # colors
        self.title_color = '#51abc2'
        self.artist_name_color = '#1b5361'
        self.text_color = '#51abc2'

        # sizes
        self.width = self.master.winfo_width()
        self.height = self.master.winfo_height()
        self.grid_height = self.height
        self.grid_width = self.width
        self.title_font_size = 12

        # texts
        self.issue_text = texts.get('MODELS_ISSUE_TEXT')
        self.title_text = texts.get('TITLE_TEXT')

        # font
        self.text_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE,
                                   weight=font.BOLD)
        self.canvas_artist_font = font.Font(family='Courier', size=10)
        self.output_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 4)

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

        # add language button
        self.language_button = self.make_switchbutton(values=texts.LANGS, default=texts.LANG)
        self.language_button.configure(width=PikaxButton.width)
        self.language_button_id = self.add_widget(widget=self.language_button, row=self.grid_height - 30,
                                                  column=self.grid_width - 250)
        self.language_button.bind('<Button-1>', self.language_button_clicked, add='+')

        # add background artist reference
        self.artist_reference = self.add_text(
            text=texts.get('MODELS_ARTIST_REFERENCE_TEXT').format(artist_name=settings.CANVAS_BACKGROUND_ARTIST_NAME),
            row=self.grid_height - 26, column=100,
            columnspan=2, font=self.canvas_artist_font,
            color=self.artist_name_color)

    def show_frame(self, name):
        if name in self.master.frames:
            frame = self.master.frames[name]
            frame.tkraise()
            import sys
            sys.stderr.write('hi')

    def save_inputs(self):
        pass

    def destroy(self):
        self.frame.destroy()

    def language_button_clicked(self, _=None):
        self.save_inputs()
        texts.set_next_lang()
        save_language()
        self.refresh = refresh(self)

    def make_frame(self, *args, **kwargs):
        return tk.Frame(master=self.master, *args, **kwargs)

    def get_cropped_image(self, image_path, focus=tk.CENTER):
        im = crop_to_dimension(open_image(image_path), focus=focus, width_ratio=self.width, height_ratio=self.height)
        im = im.resize((self.width, self.height))
        im = get_tk_image(self.frame, im, image_path)
        return im

    def set_canvas(self, image_path, focus=tk.CENTER):
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
    def grid(component, row=0, column=0, rowspan=1, columnspan=1, sticky='nsew', *args, **kwargs):
        component.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, *args, **kwargs)

    @staticmethod
    def pack(component, *args, **kwargs):
        component.pack(*args, **kwargs)

    def make_fullscreen_canvas(self):
        return tk.Canvas(self.frame, borderwidth=0, highlightthickness=0,
                         height=self.height, width=self.width, bg=settings.DEFAULT_BACKGROUND_COLOR)

    def redirect_output_to(self, text_component, text_widget=True, canvas=None, preprocess_func=None):
        import sys
        if text_widget:
            from common import StdoutTextWidgetRedirector
            sys.stdout = StdoutTextWidgetRedirector(text_component, preprocess_func=preprocess_func)
        else:
            from common import StdoutCanvasTextRedirector
            if not canvas:
                canvas = self.canvas
            sys.stdout = StdoutCanvasTextRedirector(canvas, text_component, preprocess_func=preprocess_func)

    def get_canvas_location(self, row, column, rowspan, columnspan):
        if row < 0 or row > self.grid_height:
            raise ValueError(texts.get('MODELS_INVALID_ROW_ERROR').format(row=row, grid_height=self.grid_height))
        if column < 0 or column > self.grid_width:
            raise ValueError(texts.get('MODELS_INVALID_COLUMN_ERROR').format(column=column, grid_width=self.grid_width))
        if row + rowspan < 0 or row + rowspan > self.grid_height:
            raise ValueError(
                texts.get('MODELS_INVALID_ROWSPAN_ERROR').format(rowspan=rowspan, row=row,
                                                                 grid_height=self.grid_height))
        if column + columnspan < 0 or column + columnspan > self.grid_width:
            raise ValueError(texts.get('MODELS_INVALID_COLUMNSPAN_ERROR').format(columnspan=columnspan, column=column,
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
            color = self.text_color
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
        return PikaxButton(master=self.frame, *args, **kwargs)

    def make_dropdown(self, default, choices, **kwargs):
        return PikaxDropdown(master=self.frame, default=default, choices=choices, **kwargs)

    def make_entry(self, *args, **kwargs):
        return PikaxEntry(master=self.frame, *args, **kwargs)

    def make_text(self, *args, **kwargs):
        return PikaxText(master=self.frame, *args, **kwargs)

    def make_checkbutton(self, initial=False, *args, **kwargs):
        return PikaxCheckButton(master=self.frame, initial=initial, *args, **kwargs)

    def make_switchbutton(self, values, default=None, *args, **kwargs):
        return PikaxSwitchButton(
            master=self.frame,
            values=values,
            default=default,
            *args,
            **kwargs
        )

    # common stuff
    def make_limit_text_entry(self):
        limit_choices = texts.get('LIMIT_CHOICES')
        limit_text_entry = self.make_switchbutton(limit_choices, default=limit_choices[0], width=PikaxButton.width)
        return limit_text_entry
