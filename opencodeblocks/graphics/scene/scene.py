# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB Scene """

import math
import json
from typing import List, OrderedDict, Union

from PyQt5.QtCore import QLine, QRectF
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsScene

from opencodeblocks.core.serializable import Serializable
from opencodeblocks.graphics.blocks.block import OCBBlock
from opencodeblocks.graphics.blocks.codeblock import OCBCodeBlock
from opencodeblocks.graphics.edge import OCBEdge
from opencodeblocks.graphics.scene.history import SceneHistory


class OCBScene(QGraphicsScene, Serializable):

    """ Scene for the OCB Window. """

    def __init__(self, parent=None,
            background_color:str="#393939",
            grid_color:str="#292929", grid_light_color:str="#2f2f2f",
            width:int=64000, height:int=64000,
            grid_size:int=20, grid_squares:int=5):
        Serializable.__init__(self)
        QGraphicsScene.__init__(self, parent=parent)

        self._background_color = QColor(background_color)
        self._grid_color = QColor(grid_color)
        self._grid_light_color = QColor(grid_light_color)
        self.grid_size = grid_size
        self.grid_squares = grid_squares

        self.width, self.height = width, height
        self.setSceneRect(-self.width//2, -self.height//2, self.width, self.height)
        self.setBackgroundBrush(self._background_color)

        self.history = SceneHistory(self)
    def sortedSelectedItems(self) -> List[Union[OCBBlock, OCBEdge]]:
        selected_blocks, selected_edges = [], []
        for item in self.selectedItems():
            if isinstance(item, OCBBlock):
                selected_blocks.append(item)
            if isinstance(item, OCBEdge):
                selected_edges.append(item)
        return selected_blocks, selected_edges

    def drawBackground(self, painter: QPainter, rect: QRectF):
        """ Draw the Scene background """
        super().drawBackground(painter, rect)
        self.drawGrid(painter, rect)

    def drawGrid(self, painter: QPainter, rect: QRectF):
        """ Draw the background grid """
        left = int(math.floor(rect.left()))
        top = int(math.floor(rect.top()))
        right = int(math.ceil(rect.right()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        # Compute all lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.grid_size):
            if x % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.grid_size):
            if y % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))

        # Draw the lines using the painter
        pen = QPen(self._grid_color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLines(*lines_dark)

        pen = QPen(self._grid_light_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLines(*lines_light)

    def save(self, filepath:str):
        self.save_to_json(filepath)

    def save_to_json(self, filepath:str):
        if '.' not in filepath:
            filepath += '.ipyg'

        extention_format = filepath.split('.')[-1]
        if extention_format != 'ipyg':
            raise NotImplementedError(f"Unsupported format {extention_format}")

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.serialize(), indent=4))

    def load(self, filepath:str):
        if filepath.endswith('.ipyg'):
            data = self.load_from_json(filepath)
        else:
            extention_format = filepath.split('.')[-1]
            raise NotImplementedError(f"Unsupported format {extention_format}")
        self.deserialize(data)
        self.history.checkpoint("Loaded scene")

    def load_from_json(self, filepath:str):
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())
        return data

    def serialize(self) -> OrderedDict:
        blocks = []
        edges = []
        for item in self.items():
            if isinstance(item, OCBBlock):
                blocks.append(item)
            elif isinstance(item, OCBEdge):
                edges.append(item)
        blocks.sort(key=lambda x: x.id)
        edges.sort(key=lambda x: x.id)
        return OrderedDict([
            ('id', self.id),
            ('blocks', [block.serialize() for block in blocks]),
            ('edges', [edge.serialize() for edge in edges]),
        ])

    def deserialize(self, data: OrderedDict, hashmap:dict=None, restore_id=True):
        self.clear()
        hashmap = hashmap if hashmap is not None else {}
        if restore_id:
            self.id = data['id']

        # Create blocks
        for block_data in data['blocks']:
            if block_data['block_type'] == 'base':
                block = OCBBlock()
            elif block_data['block_type'] == 'code':
                block = OCBCodeBlock()
            else:
                raise NotImplementedError()
            block.deserialize(block_data, hashmap, restore_id)
            self.addItem(block)
            hashmap.update({block_data['id']: block})

        # Create edges
        for edge_data in data['edges']:
            edge = OCBEdge()
            edge.deserialize(edge_data, hashmap, restore_id)
            self.addItem(edge)
            hashmap.update({edge_data['id']: edge})
