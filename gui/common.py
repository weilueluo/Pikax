import multiprocessing as mp
import os
import pickle
import sys
import threading
import tkinter as tk
from tkinter import END, NORMAL, DISABLED, Text, Entry, TclError

from PIL import Image, ImageTk

import settings
import texts

_screen_lock = threading.Lock()


def go_to_next_screen(src, dest):
    global _screen_lock
    if _screen_lock.locked():
        return
    with _screen_lock:
        pikax_handler = src.pikax_handler
        master = src.frame.master
        dest(master, pikax_handler)  # create new screen
        # destroy old screen
        src.destroy()


def refresh(cls_self):
    global _screen_lock
    if _screen_lock.locked():
        return
    with _screen_lock:
        exec("""
from menu import MenuScreen
from login import LoginScreen
from search import SearchScreen
from rank import RankScreen
from artist import ArtistScreen
from illustration import IllustrationScreen
        """)
        exec(f"""
new_screen = {cls_self.__class__.__name__}(cls_self.master, cls_self.pikax_handler)
        """, locals())
        cls_self.destroy()  # destroy old window
        return locals()['new_screen']


def clear_widget(widget):
    if isinstance(widget, tk.Entry):
        widget.delete(0, tk.END)
    else:  # must be tk.Text
        widget.delete(0.0, tk.END)


def clear_widgets(widgets):
    for widget in widgets:
        clear_widget(widget)


def download(target, args=(), kwargs=()):
    from download import DownloadWindow
    import texts
    kwargs['lang'] = texts.LANG  # manually remember language
    mp.Process(target=DownloadWindow, args=(target, args, kwargs)).start()


def remove_invalid_chars(string):
    return ''.join([s if ord(s) < 65565 else '#' for s in str(string)])


class StdoutTextWidgetRedirector:
    def __init__(self, text_component, preprocess_func=None):
        self.queue = mp.Queue()
        self.text_component = text_component
        self.preprocess_func = preprocess_func
        self.text_component.tag_configure('center', justify=tk.CENTER)
        threading.Thread(target=self.receiver).start()

    def receiver(self):
        try:
            while True:
                item = self.queue.get()
                self._write(*item)
        except (EOFError, BrokenPipeError) as e:
            sys.stderr.write(str(e))

    def _write(self, string, append=False):
        try:
            string = remove_invalid_chars(string)
            self.text_component.configure(state=NORMAL)

            if isinstance(self.text_component, Text):
                if append:
                    self.text_component.insert(END, '\n' + string)
                else:
                    self.text_component.delete(1.0, END)
                    self.text_component.insert(1.0, string, 'center')
                self.text_component.see(END)
            elif isinstance(self.text_component, Entry):
                self.text_component.delete(0, END)
                self.text_component.insert(0, string)
            else:
                raise TypeError(f'Writing text to invalid component: {self.text_component}')
            self.text_component.configure(state=DISABLED)
        except TclError as e:
            sys.stderr.write(str(e))

    def write(self, string, append=False):
        if self.preprocess_func is not None:
            string = self.preprocess_func(string)
        self.queue.put((string, append))

    def flush(self):
        pass


class StdoutPipeWriter:

    def __init__(self, pipe, preprocess_func=None):
        self.pipe = pipe
        self.preprocess_func = preprocess_func

    def write(self, string):
        if self.preprocess_func is not None:
            string = self.preprocess_func(string)
        self.pipe.put(string)

    def flush(self):
        pass


class StdoutCanvasTextRedirector:
    def __init__(self, canvas, text_id, preprocess_func=None):
        self.text_id = text_id
        self.canvas = canvas
        self.queue = mp.Queue()
        self.preprocess_func = preprocess_func
        threading.Thread(target=self.receiver).start()

    def receiver(self):
        while True:
            string = self.queue.get()
            self._write(string)

    def write(self, string):
        if self.preprocess_func is not None:
            string = self.preprocess_func(string)
        self.queue.put(string)

    def _write(self, string):
        try:
            self.canvas.itemconfigure(self.text_id, text=remove_invalid_chars(string))
        except TclError as e:
            self.canvas.itemconfigure(self.text_id, text=remove_invalid_chars(str(e)))

    def flush(self):
        pass


# an attempt to avoid flashing when creating new frame, failed, may be removed in the future
path_to_im = dict()


def open_image(path, use_cache=True):
    global path_to_im
    if path in path_to_im and use_cache:
        return path_to_im[path]
    im = Image.open(path)
    im.path = path
    path_to_im[path] = im
    return im


# an attempt to avoid flashing when creating new frame, failed, may be removed in the future
im_to_tk_im = dict()


def get_tk_image(master, im, path, use_cache=True):
    global im_to_tk_im
    if path in im_to_tk_im and use_cache:
        return im_to_tk_im[path]
    tk_im = ImageTk.PhotoImage(master=master, image=im)
    im_to_tk_im[path] = tk_im
    return tk_im


def crop_to_dimension(im, width_ratio, height_ratio, focus=tk.CENTER):
    transformed_width = im.height / height_ratio * width_ratio
    if transformed_width < im.width:
        width = transformed_width
        height = im.height
    else:
        height = im.width / width_ratio * height_ratio
        width = im.width

    mid = list(x / 2 for x in im.size)
    half_width = width / 2
    half_height = height / 2

    if focus == tk.CENTER:
        mid = mid
    elif focus == tk.N:
        mid[1] = half_height
    elif focus == tk.S:
        mid[1] = im.size[1] - half_height
    elif focus == tk.W:
        mid[0] = half_width
    elif focus == tk.E:
        mid[0] = im.size[0] - half_width
    else:
        raise ValueError(f'Invalid focus: {focus}')

    left = mid[0] - half_width
    upper = mid[1] - half_height
    right = mid[0] + half_width
    lower = mid[1] + half_height

    return im.crop((left, upper, right, lower))


def get_background_file_path():
    import os
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')

    return os.path.join(base_path, settings.CANVAS_BACKGROUND_PATH)


# https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def config_root(root, title, width, height):
    root.withdraw()  # hide the app before configuration
    root.geometry('{}x{}'.format(width, height))
    center(root)
    root.configure(bg=settings.DEFAULT_BACKGROUND_COLOR, borderwidth=0, highlightthickness=0)
    root.title(title)
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.after(0, root.deiconify)  # show the app again


def save_to_local(file_path, item):
    with open(file_path, 'wb') as file:
        pickle.dump(item, file, pickle.HIGHEST_PROTOCOL)


def remove_local_file(file_path):
    os.remove(file_path)


# return none and remove file if failed to load else return loaded content
def load_from_local(file_path):
    try:
        with open(file_path, 'rb') as file:
            return pickle.load(file)
    except pickle.UnpicklingError as e:
        sys.stdout.write(texts.get('FILE_CORRUPTED').format(file=file_path, msg=str(e)))
        remove_local_file(file_path)
        return None


def restore_language_if_saved(login_screen):
    if not os.path.isfile(settings.LANGUAGE_FILE):
        return login_screen
    lang = load_from_local(settings.LANGUAGE_FILE)
    if not lang:  # corrupted
        return login_screen
    import texts
    languages_available = texts.LANGS
    if lang in languages_available:
        texts.LANG = lang
        return refresh(login_screen)
    else:  # corrupted
        remove_local_file(settings.LANGUAGE_FILE)
        return login_screen


def save_language():
    import texts
    save_to_local(settings.LANGUAGE_FILE, texts.LANG)


KEY = 1046527  # a prime number https://en.wikipedia.org/wiki/List_of_prime_numbers#Lists_of_primes_by_type


def make_unreadable_when_serialized(string):
    global KEY
    enc = []
    for i in range(len(string)):
        enc.append(int(ord(string[i]) * (i + 1 + KEY)))
    return enc


def make_readable_from_unreadable(arr):
    global KEY
    dec = ''
    for i in range(len(arr)):
        dec += chr(int(arr[i] / (i + 1 + KEY)))
    return dec


#
# multiprocessing stuff below
#
def _get_num_of_processes():
    num = os.cpu_count()
    try:
        if settings.MAX_PROCESSES and settings.MAX_PROCESSES > num:
            return settings.MAX_PROCESSES
        else:
            return num
    except AttributeError:
        return num


# total must be positive
def _get_num_of_items_for_each_routine(total, num_of_routine):
    if num_of_routine < 1:
        return 1, total

    num_of_item_for_each_process = int(total / num_of_routine) + 1 if num_of_routine > 1 else int(
        total / num_of_routine)

    if num_of_item_for_each_process < 1:
        num_of_item_for_each_process = 1

    try:
        if settings.MIN_ITEMS_EACH_PROCESS and settings.MIN_ITEMS_EACH_PROCESS > num_of_item_for_each_process:
            return _get_num_of_items_for_each_routine(total, num_of_routine=num_of_routine - 1)
        else:
            return num_of_routine, num_of_item_for_each_process
    except AttributeError:
        return num_of_routine, num_of_item_for_each_process


# basically a copy of StdoutTextRedirector
# rebuild in the new process from the old queue
# to avoid pickling tk app as it is not possible
class QueueWriter:
    def __init__(self, queue):
        self.queue = queue

    def write(self, string, append=False):
        self.queue.put((string, append))

    def flush(self):
        pass


def queue_downloader(target, queue, stdout_queue, lang):
    import sys
    sys.stdout = QueueWriter(stdout_queue)
    texts.LANG = lang
    try:
        while True:
            item = queue.get()
            if item is None:
                break
            target(item)
    except (EOFError, BrokenPipeError, OSError) as e:
        sys.stderr.write(str(e))
    except MemoryError as e:
        # TODO: display a dialogue
        import sys
        sys.stdout.write(f'OUT OF MEMORY: {e}')


def concurrent_download(target, items):
    num_of_processes = _get_num_of_processes()

    queue = mp.Queue(maxsize=num_of_processes)
    processes = []
    stdout_queue = sys.stdout.queue
    for i in range(num_of_processes):
        process = mp.Process(target=queue_downloader,
                             kwargs={
                                 'target': target,
                                 'queue': queue,
                                 'stdout_queue': stdout_queue,
                                 'lang': texts.LANG
                             }
                             )
        processes.append(process)

    for process in processes:
        process.start()

    for item in items:
        queue.put(item)

    for _ in range(num_of_processes):  # tell processes to stop
        queue.put(None)

    for process in processes:
        process.join()


if __name__ == '__main__':
    s = make_unreadable_when_serialized('username')
    sys.stderr.write(str(s))
    k = make_readable_from_unreadable(s)
    sys.stderr.write(str(k))
