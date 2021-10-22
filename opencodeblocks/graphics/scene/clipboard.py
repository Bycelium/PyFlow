# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the handling an OCBScene clipboard operations. """

from typing import TYPE_CHECKING, OrderedDict
from warnings import warn

import json
from PyQt5.QtWidgets import QApplication

from opencodeblocks.graphics.blocks import OCBBlock, OCBCodeBlock
from opencodeblocks.graphics.edge import OCBEdge

if TYPE_CHECKING:
    from opencodeblocks.graphics.scene import OCBScene


class SceneClipboard():
    """ Helper object to handle clipboard operations on an OCBScene.

    Args:
        scene: Scene reference.

    """

    def __init__(self, scene:'OCBScene'):
        self.scene = scene

    def _serializeSelected(self, delete=False) -> OrderedDict:
        selected_blocks, selected_edges = self.scene.sortedSelectedItems()
        selected_sockets = {}

        for block in selected_blocks: # Gather selected sockets
            for socket in block.sockets_in + block.sockets_out:
                selected_sockets[socket.id] = socket

        for edge in selected_edges: # Filter edges that are not fully connected to selected sockets
            if edge.source_socket.id not in selected_sockets or \
                    edge.destination_socket.id not in selected_sockets:
                selected_edges.remove(edge)

        data = OrderedDict([
            ('blocks', [block.serialize() for block in selected_blocks]),
            ('edges', [edge.serialize() for edge in selected_edges])
        ])

        if delete: # Remove selected items
            self.scene.views()[0].deleteSelected()

        return data

    def _find_bbox_center(self, blocks_data):
        xmin, xmax, ymin, ymax = 0, 0, 0, 0
        for block_data in blocks_data:
            x, y = block_data['position']
            if x < xmin:
                xmin = x
            if x > xmax:
                xmax = x
            if y < ymin:
                ymin = y
            if y > ymax:
                ymax = y
        return (xmin + xmax) / 2, (ymin + ymax) / 2

    def _deserializeData(self, data:OrderedDict):
        hashmap = {}

        view = self.scene.views()[0]
        mouse_pos = view.lastMousePos

        # Finding pasting bbox center
        bbox_center_x, bbox_center_y = self._find_bbox_center(data['blocks'])
        offset_x, offset_y = mouse_pos.x() - bbox_center_x, mouse_pos.y() - bbox_center_y

        # Create blocks
        for block_data in data['blocks']:
            block_type = block_data['block_type']
            if block_type == 'base':
                block = OCBBlock()
            elif block_type == 'code':
                block = OCBCodeBlock()
            else:
                raise NotImplementedError(f'Unsupported block type: {block_type}')
            block.deserialize(block_data, hashmap, restore_id=False)

            block_pos = block.pos()
            block.setPos(block_pos.x() + offset_x, block_pos.y() + offset_y)

            self.scene.addItem(block)
            hashmap.update({block.id: block})

        # Create edges
        for edge_data in data['edges']:
            edge = OCBEdge()
            edge.deserialize(edge_data, hashmap, restore_id=False)
            self.scene.addItem(edge)
            hashmap.update({edge_data['id']: edge})

        self.scene.history.checkpoint('Desiralized elements into scene')

    def _store(self, data:OrderedDict):
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def _gatherData(self) -> str:
        str_data = QApplication.instance().clipboard().text()
        try:
            return json.loads(str_data)
        except ValueError as valueerror:
            warn(f"Clipboard text could not be loaded into json data: {valueerror}")
            return

    def cut(self):
        self._store(self._serializeSelected(delete=True))

    def copy(self):
        self._store(self._serializeSelected(delete=False))

    def paste(self):
        self._deserializeData(self._gatherData())
