# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Utilities functions for integration testing.
"""

import os
import asyncio
from typing import Callable

import threading
from queue import Queue
from qtpy.QtWidgets import QApplication
import pytest_check as check

from opencodeblocks.graphics.window import OCBWindow

STOP_MSG = "stop"
CHECK_MSG = "check"


class CheckingQueue(Queue):
    def check_equal(self, a, b, msg=""):
        self.put([CHECK_MSG, a, b, msg])

    def stop(self):
        self.put([STOP_MSG])


def apply_function_inapp(window: OCBWindow, run_func: Callable):

    if os.name == "nt":  # If on windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    QApplication.processEvents()
    msgQueue = CheckingQueue()
    t = threading.Thread(target=run_func, args=(msgQueue,))
    t.start()

    stop = False
    while not stop:
        QApplication.processEvents()
        if not msgQueue.empty():
            msg = msgQueue.get()
            if msg[0] == CHECK_MSG:
                check.equal(msg[1], msg[2], msg[3])
            elif msg[0] == STOP_MSG:
                stop = True
    t.join()
    window.close()
