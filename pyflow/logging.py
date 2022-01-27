from ast import For
from time import time
import logging
from functools import wraps
from unittest.mock import DEFAULT
from colorama import Fore, Style


def log_init_time(logger: logging.Logger, level=logging.DEBUG):
    def inner(func):
        @wraps(func)
        def wrapper_func(self: type, *args, **kwargs):
            init_time = time()
            func(self, *args, **kwargs)
            # TODO: Make this more robust
            class_name = str(self).split(" ")[0].split(".")[-1]
            logger.log(
                level, "Built %s in %.3fs", class_name, time() - init_time, stacklevel=2
            )

        return wrapper_func

    return inner


def get_logger(name: str):
    return logging.getLogger(name)


class PyflowHandler(logging.StreamHandler):

    COLOR_BY_LEVEL = {
        "DEBUG": Fore.GREEN,
        "INFO": Fore.BLUE,
        "WARNING": Fore.LIGHTRED_EX,
        "WARN": Fore.YELLOW,
        "ERROR": Fore.RED,
        "FATAL": Fore.RED,
        "CRITICAL": Fore.RED,
    }

    def emit(self, record):
        record.pathname = "pyflow" + record.pathname.split("pyflow")[-1]

        level_color = self.COLOR_BY_LEVEL.get(record.levelname)
        if level_color:
            record.levelname = level_color + record.levelname + Style.RESET_ALL
        return super().emit(record)
