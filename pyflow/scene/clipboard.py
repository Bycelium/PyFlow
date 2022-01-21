# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the handling of scene clipboard operations. """

from typing import TYPE_CHECKING, OrderedDict, Union
from warnings import warn

from pyflow.core.edge import Edge

if TYPE_CHECKING:
    from pyflow.scene import Scene


class BlocksClipboard:

    """Helper object to handle clipboard operations on blocks."""

    def __init__(self):
        """Helper object to handle clipboard operations on blocks."""
        self.blocks_data: Union[None, OrderedDict] = None

    def cut(self, scene: "Scene"):
        """Cut the selected items and put them into clipboard."""
        self.scene = scene
        self._store(self._serializeSelected(delete=True))

    def copy(self, scene: "Scene"):
        """Copy the selected items into clipboard."""
        self.scene = scene
        self._store(self._serializeSelected(delete=False))

    def paste(self, scene: "Scene"):
        """Paste the items in clipboard into the current scene."""
        self.scene = scene
        data = self._gatherData()
        if data is not None:
            self._deserializeData(data)

    def _serializeSelected(self, delete=False) -> OrderedDict:
        """Serialize the items in the scene"""
        selected_blocks, selected_edges = self.scene.sortedSelectedItems()
        selected_sockets = {}

        # Gather selected sockets
        for block in selected_blocks:
            for socket in block.sockets_in + block.sockets_out:
                selected_sockets[socket.id] = socket

        # Filter edges that are not fully connected to selected sockets
        for edge in selected_edges:
            if (
                edge.source_socket.id not in selected_sockets
                or edge.destination_socket.id not in selected_sockets
            ):
                selected_edges.remove(edge)

        data = OrderedDict(
            [
                ("blocks", [block.serialize() for block in selected_blocks]),
                ("edges", [edge.serialize() for edge in selected_edges]),
            ]
        )

        if delete:  # Remove selected items
            self.scene.views()[0].deleteSelected()

        return data

    def _find_bbox_center(self, blocks_data):
        xmin = min(block["position"][0] for block in blocks_data)
        xmax = max(block["position"][0] + block["width"] for block in blocks_data)
        ymin = min(block["position"][1] for block in blocks_data)
        ymax = max(block["position"][1] + block["height"] for block in blocks_data)
        return (xmin + xmax) / 2, (ymin + ymax) / 2

    def _deserializeData(self, data: OrderedDict, set_selected=True):
        """Deserialize the items and put them in the scene"""

        if data is None:
            return

        hashmap = {}

        view = self.scene.views()[0]
        mouse_pos = view.lastMousePos
        if set_selected:
            self.scene.clearSelection()

        # Finding pasting bbox center
        bbox_center_x, bbox_center_y = self._find_bbox_center(data["blocks"])
        offset_x, offset_y = (
            mouse_pos.x() - bbox_center_x,
            mouse_pos.y() - bbox_center_y,
        )

        # Create blocks
        for block_data in data["blocks"]:
            block = self.scene.create_block(block_data, hashmap, restore_id=False)
            if set_selected:
                block.setSelected(True)
            block.setPos(block.x() + offset_x, block.y() + offset_y)

        # Create edges
        for edge_data in data["edges"]:
            edge = Edge()
            edge.deserialize(edge_data, hashmap, restore_id=False)

            if set_selected:
                edge.setSelected(True)
            self.scene.addItem(edge)
            hashmap.update({edge_data["id"]: edge})

        self.scene.history.checkpoint(
            "Desiralized elements into scene", set_modified=True
        )

    def _store(self, data: OrderedDict):
        """Store the data in the clipboard if it is valid."""

        if "blocks" not in data or not data["blocks"]:
            self.blocks_data = None
            return

        self.blocks_data = data

    def _gatherData(self) -> Union[OrderedDict, None]:
        """Return the data stored in the clipboard."""
        if self.blocks_data is None:
            warn(f"No object is loaded")
        return self.blocks_data
