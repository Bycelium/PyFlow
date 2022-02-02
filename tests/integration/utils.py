# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

"""
Utilities functions for integration testing.
"""

from typing import Callable, Tuple

import os
import warnings
import threading
import time
from queue import Queue

import pytest_check as check
import asyncio

from PyQt5.QtWidgets import QApplication, QGraphicsItem
from PyQt5.QtCore import QPointF, QPoint

from pyflow.graphics.widget import Widget
from pyflow.graphics.window import Window

if os.name == "nt":  # If on windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

STOP_MSG = "stop"
CHECK_MSG = "check"
RUN_MSG = "run"


class InAppTest:
    def start_app(self):
        self.window = Window()
        self.widget = Widget()
        self.subwindow = self.window.mdiArea.addSubWindow(self.widget)
        self.subwindow.show()

    def get_global_pos(
        self, item: QGraphicsItem, rel_pos: Tuple[int] = (0, 0)
    ) -> QPoint:
        if isinstance(item.width, (int, float)):
            width = item.width
        else:
            width = item.width()
        if isinstance(item.height, (int, float)):
            height = item.height
        else:
            height = item.height()

        pos = QPointF(
            item.pos().x() + rel_pos[0] * width,
            item.pos().y() + rel_pos[1] * height,
        )
        pos_global = self.widget.view.mapFromScene(pos)
        pos_global = self.widget.view.mapToGlobal(pos_global)
        return pos_global


class CheckingQueue(Queue):
    def check_equal(self, a, b, msg=""):
        self.put([CHECK_MSG, a, b, msg])

    def run_lambda(self, func: Callable, *args, **kwargs):
        self.put([RUN_MSG, func, args, kwargs])

    def stop(self):
        self.put([STOP_MSG])


class ExceptionForwardingThread(threading.Thread):
    """A Thread class that forwards the exceptions to the calling thread."""

    def __init__(self, *args, **kwargs):
        """Create an exception forwarding thread."""
        super().__init__(*args, **kwargs)
        self.exeption = None

    def run(self):
        """Code ran in another thread."""
        try:
            super().run()
        except Exception as e:
            self.exeption = e

    def join(self):
        """Used to sync the thread with the caller."""
        super().join()
        print("except: ", self.exeption)
        if self.exeption is not None:
            raise self.exeption


def apply_function_inapp(window: Window, run_func: Callable):
    QApplication.processEvents()
    msgQueue = CheckingQueue()
    thread = ExceptionForwardingThread(target=run_func, args=(msgQueue,))
    thread.start()

    stop = False
    deadCounter = 0

    while not stop:
        time.sleep(1 / 30)  # 30 fps
        QApplication.processEvents()
        if not msgQueue.empty():
            msg = msgQueue.get()
            if msg[0] == CHECK_MSG:
                check.equal(msg[1], msg[2], msg[3])
            elif msg[0] == STOP_MSG:
                stop = True
            elif msg[0] == RUN_MSG:
                msg[1](*msg[2], **msg[3])

        if not thread.is_alive() and not stop:
            deadCounter += 1
        if deadCounter >= 3:
            # Test failed, close was not called
            warnings.warn(
                "Warning: you need to call CheckingQueue.stop() at the end of your test !"
            )
            break
    thread.join()
