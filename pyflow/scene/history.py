# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the handling a scene history. """

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pyflow.scene import Scene


class SceneHistory:
    """Helper object to handle undo/redo operations on an Scene.

    Args:
        scene: Scene reference.
        max_stack: Maximum size of the history stack (number of available undo).

    """

    def __init__(self, scene: "Scene", max_stack: int = 50):
        self.scene = scene
        self.history_stack = []
        self.current = -1
        self.max_stack = max_stack

    def undo(self):
        """Undo the last action by moving the current stamp backward and restoring."""
        if len(self.history_stack) > 0 and self.current > 0:
            self.current -= 1
            self.restore()

    def redo(self):
        """Redo the last undone action by moving the current stamp forward and restoring."""
        if len(self.history_stack) > 0 and self.current + 1 < len(self.history_stack):
            self.current += 1
            self.restore()

    def checkpoint(self, description: str, set_modified=True):
        """Store a snapshot of the scene in the history stack.

        Args:
            description: Description given to this checkpoint.
            set_modified: Whether the scene should be considered modified.

        """
        history_stamp = {"description": description, "snapshot": self.scene.serialize()}
        self.store(history_stamp)
        if set_modified:
            self.scene.has_been_modified = True

    def store(self, data: Any):
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

    def restore(self):
        """Restore the scene using the snapshot pointed by current in the history stack."""
        if len(self.history_stack) >= 0 and self.current >= 0:
            stamp = self.history_stack[self.current]
            snapshot = stamp["snapshot"]
            self.scene.deserialize(snapshot)
