# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Utilities functions for integration testing.
"""

from typing import Callable

import os
import asyncio
import threading
import time
from queue import Queue

from qtpy.QtWidgets import QApplication
import pytest_check as check
import warnings
from opencodeblocks.graphics.widget import OCBWidget

from opencodeblocks.graphics.window import OCBWindow

STOP_MSG = "stop"
CHECK_MSG = "check"
RUN_MSG = "run"


class CheckingQueue(Queue):
    def check_equal(self, a, b, msg=""):
        self.put([CHECK_MSG, a, b, msg])

    def run_lambda(self, func: Callable, *args, **kwargs):
        self.put([RUN_MSG, func, args, kwargs])

    def stop(self):
        self.put([STOP_MSG])

class ExceptionForwardingThread(threading.Thread):
    """ A Thread class that forwards the exceptions to the calling thread """
    def __init__(self, *args, **kwargs):
        """ Create an exception forwarding thread """
        super().__init__(*args, **kwargs)
        self.e = None

    def run(self):
        """ Code ran in another thread """
        try:
            super().run()
        except Exception as e:
            self.e = e

    def join(self):
        """ Used to sync the thread with the caller """
        super().join()
        print("except: ",self.e)
        if self.e != None:
            raise self.e


def start_app(obj):
    """ Create a new app for testing """
    obj.window = OCBWindow()
    obj.ocb_widget = OCBWidget()
    obj.subwindow = obj.window.mdiArea.addSubWindow(obj.ocb_widget)
    obj.subwindow.show()

def apply_function_inapp(window: OCBWindow, run_func: Callable):

    if os.name == "nt":  # If on windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    QApplication.processEvents()
    msgQueue = CheckingQueue()
    t = ExceptionForwardingThread(target=run_func, args=(msgQueue,))
    t.start()

    stop = False
    deadCounter = 0

    while not stop:
        time.sleep(1 / 30) # 30 fps
        QApplication.processEvents()
        if not msgQueue.empty():
            msg = msgQueue.get()
            if msg[0] == CHECK_MSG:
                check.equal(msg[1], msg[2], msg[3])
            elif msg[0] == STOP_MSG:
                stop = True
            elif msg[0] == RUN_MSG:
                msg[1](*msg[2], **msg[3])

        if not t.is_alive() and not stop:
            deadCounter += 1
        if deadCounter >= 3:
            # Test failed, close was not called
            warnings.warn("Warning: you need to call CheckingQueue.stop() at the end of your test !")
            break
    t.join()
