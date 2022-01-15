# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the handling an history of operations. """

from typing import Any, List


class History:
    """Helper object to handle undo/redo operations.

    Args:
        max_stack: Maximum size of the history stack (number of available undo).

    """

    def __init__(self, max_stack: int = 50):
        self.history_stack: List[Any] = []
        self.current: int = -1
        self.max_stack: int = max_stack

    def undo(self) -> None:
        """Undo the last action by moving the current stamp backward and restoring."""
        if self.history_stack and self.current > 0:
            self.current -= 1
            self.restore()

    def redo(self) -> None:
        """Redo the last undone action by moving the current stamp forward and restoring."""
        if self.history_stack and self.current + 1 < len(self.history_stack):
            self.current += 1
            self.restore()

    def store(self, data: Any) -> None:
        """Store new data in the history stack, updating current checkpoint.
        Remove data that would be forward in the history stack.

        Args:
            data: Data to store in the history stack.

        """
        if self.current + 1 < len(self.history_stack):
            self.history_stack = self.history_stack[0 : self.current + 1]

        self.history_stack.append(data)

        if len(self.history_stack) > self.max_stack:
            self.history_stack.pop(0)

        self.current = min(self.current + 1, len(self.history_stack) - 1)

    def restored_data(self) -> Any:
        """
        Return the snapshot pointed by current in the history stack.
        Return None if there is nothing pointed to.
        """
        if len(self.history_stack) >= 0 and self.current >= 0:
            data = self.history_stack[self.current]
            return data
        return None

    def restore(self) -> None:
        """
        Empty function to be overriden
        Contains the behavior to be adopted when a state is restored
        """
        raise NotImplementedError
