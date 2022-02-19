# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the Executable abstract class."""

from enum import Enum


class ExecutableState(Enum):
    """Enumeration of possible states of an Executable."""

    IDLE = 0
    RUNNING = 1
    PENDING = 2
    DONE = 3
    CRASHED = 4


class Executable:
    """Executable object in pyflow."""

    def __init__(self) -> None:
        """Executable object in pyflow."""
        self._run_state = ExecutableState.IDLE

    @property
    def run_state(self) -> ExecutableState:
        """The current state of the Executable."""
        return self._run_state

    @run_state.setter
    def run_state(self, value: ExecutableState):
        assert isinstance(value, ExecutableState)
        self._run_state = value
        # Update to force repaint if available
        if hasattr(self, "update"):
            self.update()
