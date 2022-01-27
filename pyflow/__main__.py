# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>
# pylint:disable=wrong-import-position, protected-access

""" Pyflow main module. """

import os
import sys

import argparse
import logging

import asyncio
from colorama import init, Fore, Style

init()
if os.name == "nt":  # If on windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from PyQt5.QtWidgets import QApplication

from pyflow.graphics.window import Window
from pyflow import __version__
from pyflow.logging import PyflowHandler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help="path to a file to open")
    parser.add_argument(
        "-v",
        "--verbose",
        type=str,
        choices=logging._nameToLevel.keys(),
        help="set logging level",
        default="INFO",
    )
    args = parser.parse_args()

    # Debug flag will lower logging level to DEBUG
    log_level = logging._nameToLevel[args.verbose.upper()]
    logging.basicConfig(
        filename="pyflow.log",
        level=logging.INFO,
    )
    pyflow_logger = logging.getLogger("pyflow")
    pyflow_logger.setLevel(log_level)

    stream_formater = logging.Formatter(
        "%(asctime)s|%(levelname)s| %(pathname)s#%(lineno)d: > %(message)s",
        datefmt="%H:%M:%S",
    )
    stream_handler = PyflowHandler()
    stream_handler.setFormatter(stream_formater)
    pyflow_logger.addHandler(stream_handler)

    if log_level <= logging.DEBUG:
        print(Fore.GREEN + "-" * 15 + " DEBUG MODE ON " + "-" * 15 + Style.RESET_ALL)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    wnd = Window()

    if args.path:
        wnd.createNewMdiChild(args.path)

    wnd.setWindowTitle(f"Pyflow {__version__}")
    wnd.show()
    sys.exit(app.exec_())
