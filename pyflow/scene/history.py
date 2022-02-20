# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the handling an OCBScene history. """

from typing import TYPE_CHECKING, Optional
import logging

from pyflow.core.history import History

if TYPE_CHECKING:
    from pyflow.scene import Scene

logger = logging.getLogger(__name__)


class SceneHistory(History):
    """Helper object to handle undo/redo operations on an Scene.

    Args:
        scene: Scene reference.
        max_stack: Maximum size of the history stack (number of available undo).

    """

    def __init__(self, scene: "Scene", max_stack: int = 50):
        self.scene = scene
        self._hash: Optional[str] = None
        super().__init__(max_stack)

    def checkpoint(
        self, description: str, set_modified=True, erase_previous_checkpoints=False
    ):
        """Store a snapshot of the scene in the history stack.

        Args:
            description: Description given to this checkpoint.
            set_modified: Whether the scene should be considered modified.
            erase_previous_checkpoints: Whether the previous checkpoints should be erased

        """

        serialized_scene = self.scene.serialize()

        new_serialized_scene_hash = hash(str(serialized_scene))
        if not self.should_checkpoint(new_serialized_scene_hash):
            return

        if erase_previous_checkpoints:
            self.history_stack = []

        self._hash = new_serialized_scene_hash

        history_stamp = {
            "description": description,
            "snapshot": serialized_scene,
        }
        self.store(history_stamp)
        if set_modified:
            self.scene.has_been_modified = True

    def restore(self):
        """Restore the scene using the snapshot pointed by current in the history stack."""

        stamp = self.restored_data()

        if stamp is not None:
            snapshot = stamp["snapshot"]
            logger.debug("Restored [%s]: %s", self.current, stamp["description"])
            self.scene.deserialize(snapshot)

    def should_checkpoint(self, new_serialized_scene_hash: str) -> bool:
        """Return true if a checkpoint should be created.

        This is not the case when the previous checkpoint is the same as the new one.
        This is the case if there was no previous hash
        (as it is the case when the scene is first loaded)."""

        if self._hash is None:
            return True

        return self._hash != new_serialized_scene_hash
