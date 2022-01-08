# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the handling an OCBScene history. """

from typing import TYPE_CHECKING

from pyflow.core.history import History

if TYPE_CHECKING:
    from pyflow.scene import Scene


class SceneHistory(History):
    """Helper object to handle undo/redo operations on an Scene.

    Args:
        scene: Scene reference.
        max_stack: Maximum size of the history stack (number of available undo).

    """

    def __init__(self, scene: "Scene", max_stack: int = 50):
        self.scene = scene
        super().__init__(max_stack)

    def checkpoint(self, description: str, set_modified=True):
        """Store a snapshot of the scene in the history stack.

        Args:
            description: Description given to this checkpoint.
            set_modified: Whether the scene should be considered modified.

        """
        history_stamp = {
            "description": description,
            "snapshot": self.scene.serialize(),
        }
        self.store(history_stamp)
        if set_modified:
            self.scene.has_been_modified = True

    def restore(self):
        """Restore the scene using the snapshot pointed by current in the history stack."""

        stamp = self.restored_data()

        if stamp is not None:
            snapshot = stamp["snapshot"]
            self.scene.deserialize(snapshot)
