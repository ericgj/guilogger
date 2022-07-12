import logging
import logging.handlers
from queue import Queue
import sys
from threading import Thread
from time import sleep
from tkinter.font import Font
from tkinter.scrolledtext import ScrolledText
from tkinter import Tk, Text
from tkinter import ttk

LOGGING_DONE = logging.INFO + 5
MAX_LABEL_LENGTH = 500

def log_done(logger, msg: str = 'Done.'):
    logger.log(LOGGING_DONE, msg)

def app(*, level=logging.NOTSET, formatter=logging.Formatter(), title=sys.argv[0], max_steps=100):
    def _app(fn):
        def __app(*args):
            handler = TkLogHandler(level=level, title=title, max_steps=max_steps)
            handler.setFormatter(formatter)
            handler.setLevel(level)

            queue = Queue()
            queue_handler = logging.handlers.QueueHandler(queue)
            listener = logging.handlers.QueueListener(queue, handler, respect_handler_level=True)
            listener.start()

            logging.basicConfig()  # best to do from main thread

            cli_thread = Thread(
                 target=fn, 
                 name=title, 
                 args=args, 
                 kwargs={'log_handler': queue_handler},
            )
            try:
                cli_thread.start()
                handler.start()
                cli_thread.join()
            finally:
                listener.stop()

        return __app
    return _app


class App(Tk):
    def __init__(self, *, title: str, max_steps: int):
        super().__init__()
        self.max_steps = max_steps
        self.cur_steps = 0
        self.logs = []
        self.show_log = False

        self.title(title)
        # self.geometry('500x100')
        self.frame = ttk.Frame(self)
        self.progress = ttk.Progressbar(
            self.frame,
            orient='horizontal',
            value=self.cur_steps,
            maximum=max_steps,
            mode='determinate',
        )
        self.label = WrappingLabel(self.frame, text="", width=100)
        self.button_frame = ttk.Frame(self.frame)
        self.ok_button = ttk.Button(self.button_frame, text="Ok", command=self.destroy)
        self.log_button = ttk.Button(self.button_frame, text="Show log", command=self.toggle_log)
        self.log_copy_button = ttk.Button(self.button_frame, text="Copy log", command=self.copy_log)
        self.log_text_frame = ttk.Frame(self.frame, height=200)
        self.log_text_label = Text(
            self.log_text_frame, 
            font=Font(self.frame, family="Courier", size=10), 
            wrap='word',
            state='disabled',
        )
        self.log_text_scrollbar = ttk.Scrollbar(
            self.log_text_frame, 
            orient='vertical', 
            command=self.log_text_label.yview
        )
        self.log_text_label['yscrollcommand'] = self.log_text_scrollbar.set

        self.init_pack_elements()

        s = ttk.Style()
        s.theme_use('clam')
        s.configure('default.Horizontal.TProgressbar', foreground='green', background='green')
        s.configure('warning.Horizontal.TProgressbar', foreground='yellow', background='yellow')
        s.configure('error.Horizontal.TProgressbar', foreground='red', background='red')


    @property
    def has_warnings(self) -> bool:
        return any( 
            (level, msg, log_msg) 
            for (level, msg, log_msg) in self.logs 
            if level >= logging.WARNING and level < logging.ERROR
        )

    @property
    def log_text(self) -> str:
        return "\n".join([log_msg for (_,_,log_msg) in self.logs])

    def add_log(self, level: int, msg: str, log_msg: str):
        self.logs.append((level, msg, log_msg))

    def init_pack_elements(self):
        self.frame.pack(fill="both", expand=True)
        self.progress.pack(fill="x", padx=10, pady=5)
        self.label.pack(fill="x", padx=10, pady=5, expand=True)
        self.button_frame.pack(fill="x", padx=10, pady=5)
        self.ok_button.pack(side="left")
        self.log_button.pack(side="left")
        self.log_copy_button.pack(side="left")
        self.geometry("")

    def update_elements(self):
        self.log_text_label.configure(state='normal')  # enable setting text in widget
        self.log_text_label.replace('1.0','end',self.log_text)
        self.log_text_label.configure(state='disabled')
        if self.show_log:
            self.log_button.configure(text="Hide log")
            self.log_text_frame.forget()
            self.log_text_frame.pack(fill="x", expand=True, padx=10, pady=5)
            self.log_text_label.pack(fill="both", side="left", expand=True)
            self.log_text_scrollbar.pack(fill="both", side="left", expand=True)
            self.log_text_label.yview('end')  # scroll to bottom
        else:
            self.log_button.configure(text="Show log")
            self.log_text_frame.forget()
        self.geometry("")

    def toggle_log(self):
        self.show_log = not self.show_log
        self.update_elements()

    def copy_log(self):
        self.clipboard_clear()
        self.clipboard_append(self.log_text)

    def display_status(self, msg: str):
        new_steps = min(1, self.max_steps - self.cur_steps - 0.001)
        if new_steps > 0:
            self.progress.step(new_steps)
            self.cur_steps = self.cur_steps + new_steps
        if self.has_warnings:
            self.progress.configure(style='warning.Horizontal.TProgressbar')
        else:
            self.progress.configure(style='default.Horizontal.TProgressbar')
        self.label.config(text=ellipsis(MAX_LABEL_LENGTH,msg))
        self.update_elements()

    def display_done(self, msg: str):
        new_steps = self.max_steps - self.cur_steps - 0.001
        if new_steps > 0:
            self.progress.step(new_steps)
            self.cur_steps = self.cur_steps + new_steps
        if self.has_warnings:
            self.progress.configure(style='warning.Horizontal.TProgressbar')
        else:
            self.progress.configure(style='default.Horizontal.TProgressbar')
        self.label.config(text=ellipsis(MAX_LABEL_LENGTH,msg))
        self.update_elements()
        
    def display_error(self, msg: str):
        new_steps = self.max_steps - self.cur_steps - 0.001
        if new_steps > 0:
            self.progress.step(new_steps)
            self.cur_steps = self.cur_steps + new_steps
        self.progress.configure(style='error.Horizontal.TProgressbar')
        self.label.config(text=ellipsis(MAX_LABEL_LENGTH,f"ERROR: {msg}"))
        self.update_elements()

class WrappingLabel(ttk.Label):
    def __init__(self, master: None, **kwargs):
        ttk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda _: self.configure(wraplength=self.winfo_width()))


class TkLogHandler(logging.Handler):
    def __init__(self, level: int, *, title: str, max_steps: int):
        super().__init__(level)
        self.app = App(title=title, max_steps=max_steps)
        
    def start(self):
        self.app.mainloop()

    def emit(self, record):
        level = record.levelno
        msg = record.message
        log_msg = self.format(record)
        self.app.add_log(level, msg, log_msg)
        if level >= logging.ERROR:
            self.app.display_error(msg) 
        elif level == LOGGING_DONE:
            self.app.display_done(msg)
        else:
           self.app.display_status(msg)



def ellipsis(length: int, s: str) -> str:
    return s if len(s) <= length else f"{s[0:(length-3)]}..."
