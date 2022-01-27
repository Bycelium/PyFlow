# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

"""Utilitaries for logging in Pyflow."""

from time import time
import logging
from functools import wraps
from colorama import Fore, Style


def log_init_time(logger: logging.Logger, level=logging.DEBUG):
    """Decorator for logging an class init time."""

    def inner(func):
        @wraps(func)
        def wrapper_func(self: type, *args, **kwargs):
            init_time = time()
            func(self, *args, **kwargs)
            class_name = str(self).split(" ", maxsplit=1)[0].split(".")[-1]
            logger.log(
                level, "Built %s in %.3fs", class_name, time() - init_time, stacklevel=2
            )

        return wrapper_func

    return inner


def get_logger(name: str) -> logging.Logger:
    """Get the logger for the current module given it's name.

    Args:
        name (str): Name of the module usualy obtained using '__main___'

    Returns:
        logging.Logger: Logger for the given module name.
    """
    return logging.getLogger(name)


class PyflowHandler(logging.StreamHandler):

    """Custom logging handler for Pyflow."""

    COLOR_BY_LEVEL = {
        "DEBUG": Fore.GREEN,
        "INFO": Fore.BLUE,
        "WARNING": Fore.LIGHTRED_EX,
        "WARN": Fore.YELLOW,
        "ERROR": Fore.RED,
        "FATAL": Fore.RED,
        "CRITICAL": Fore.RED,
    }

    def emit(self, record: logging.LogRecord):
        record.pathname = "pyflow" + record.pathname.split("pyflow")[-1]

        level_color = self.COLOR_BY_LEVEL.get(record.levelname)
        if level_color:
            record.levelname = level_color + record.levelname + Style.RESET_ALL
        return super().emit(record)
