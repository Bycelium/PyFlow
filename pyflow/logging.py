# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

"""Utilitaries for logging in Pyflow."""

from time import time
import logging
from functools import wraps
from colorama import Fore, Style


def log_init_time(logger: logging.Logger, level=logging.DEBUG):
    """Decorator for logging a class init time."""

    def inner(func):
        """Inner decorator for logging a class init time."""

        @wraps(func)
        def wrapper_func(self: type, *args, **kwargs):
            """Wrapper for logging a class init time."""
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
        record.levelname = fill_size(record.levelname, 8)
        if level_color:
            record.levelname = level_color + record.levelname + Style.RESET_ALL
        return super().emit(record)


def fill_size(text: str, size: int, filler: str = " "):
    """Make a text fill a given size using a given filler.

    Args:
        text (str): Text to fit in given size.
        size (int): Given size to fit text in.
        filler (str, optional): Character to fill with if place there is. Defaults to " ".

    Raises:
        ValueError: The given filler is not a single character.

    Returns:
        str: A string containing the text and filler of the given size.
    """
    if len(filler) > 1:
        raise ValueError(
            f"Given filler was more than one character ({len(filler)}>1): {filler}"
        )
    if len(text) < size:
        missing_size = size - len(text)
        return filler + text + filler * (missing_size - 1)
    return text[:size]
