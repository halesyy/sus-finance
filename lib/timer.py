

import threading

def interval(func, sec):
    def func_wrapper():
        interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t
