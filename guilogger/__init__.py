import logging
import logging.handlers
from queue import Queue
import sys
from threading import Thread
from time import sleep
from tkinter import Tk
from tkinter import ttk

LOGGING_DONE = logging.INFO + 5

def log_done(logger, msg: str = 'Done.'):
    logger.log(LOGGING_DONE, msg)

def app(*, level=logging.NOTSET, title=sys.argv[0], max_steps=100):
    def _app(fn):
        def __app(*args):
            handler = TkLogHandler(level=level, title=title, max_steps=max_steps)
            handler.setFormatter(logging.Formatter())
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
        self.title(title)
        self.geometry('500x100')
        self.frame = ttk.Frame(self)
        self.progress = ttk.Progressbar(
            self.frame,
            orient='horizontal',
            value=self.cur_steps,
            maximum=max_steps,
            mode='determinate',
        )
        self.label = ttk.Label(self.frame, text="")
        self.ok_button = ttk.Button(self.frame, text="Ok", command=self.destroy)
        
        self.frame.pack(fill="both")
        self.progress.pack(fill="x", padx=10, pady=5)
        self.label.pack(fill="x", padx=10, pady=5)
        self.ok_button.pack(side="left", padx=10, pady=5)

        s = ttk.Style()
        s.theme_use('clam')
        s.configure('default.Horizontal.TProgressbar', foreground='green', background='green')
        s.configure('error.Horizontal.TProgressbar', foreground='red', background='red')


    def display_status(self, msg: str, log_msg: str):
        new_steps = min(1, self.max_steps - self.cur_steps - 0.001)
        if new_steps > 0:
            self.progress.step(new_steps)
            self.cur_steps = self.cur_steps + new_steps
        self.progress.configure(style='default.Horizontal.TProgressbar')
        self.label.config(text=msg)

    def display_done(self, msg: str):
        new_steps = self.max_steps - self.cur_steps - 0.001
        if new_steps > 0:
            self.progress.step(new_steps)
            self.cur_steps = self.cur_steps + new_steps
        self.progress.configure(style='default.Horizontal.TProgressbar')
        self.label.config(text=msg)
        
    def display_error(self, msg: str, log_msg: str):
        new_steps = self.max_steps - self.cur_steps - 0.001
        if new_steps > 0:
            self.progress.step(new_steps)
            self.cur_steps = self.cur_steps + new_steps
        self.progress.configure(style='error.Horizontal.TProgressbar')
        self.label.config(text=f"ERROR: {msg}")


class TkLogHandler(logging.Handler):
    def __init__(self, level: int, *, title: str, max_steps: int):
        super().__init__(level)
        self.app = App(title=title, max_steps=max_steps)
        
    def start(self):
        self.app.mainloop()

    def emit(self, record):
        msg = record.message
        log_msg = record.getMessage()
        if record.levelno >= logging.ERROR:
            self.app.display_error(msg, log_msg) 
        elif record.levelno == LOGGING_DONE:
            self.app.display_done(msg)
        else:
           self.app.display_status(msg, log_msg)
        self.app.label.config(text = msg)




