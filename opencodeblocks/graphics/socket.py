# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for OCB Sockets """

from __future__ import annotations
from typing import Optional, OrderedDict

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from opencodeblocks.core.serializable import Serializable


class OCBSocket(QGraphicsItem, Serializable):

    def __init__(self, block:'OCBBlock', socket_type:str='undefined', radius:float=6.0,
            color:str='#FF55FFF0', linewidth:float=1.0, linecolor:str='#FF000000'):
        Serializable.__init__(self)
        self.block = block
        QGraphicsItem.__init__(self, parent=self.block)

        self.edges = []
        self.socket_type = socket_type

        self.radius = radius
        self._pen = QPen(QColor(linecolor))
        self._pen.setWidth(linewidth)
        self._brush = QBrush(QColor(color))

        self.metadata = {
            'radius': radius,
            'color': color,
            'linewidth': linewidth,
            'linecolor': linecolor,
        }

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)

    def remove(self):
        for edge in self.edges:
            edge.remove()
        scene = self.scene()
        if scene is not None:
            scene.removeItem(self)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
            widget: Optional[QWidget]=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        r = self.radius
        painter.drawEllipse(-r, -r, 2*r, 2*r)

    def boundingRect(self) -> QRectF:
        r = self.radius
        return QRectF(-r, -r, 2*r, 2*r)

    def serialize(self) -> OrderedDict:
        metadata = OrderedDict(sorted(self.metadata.items()))
        return OrderedDict([
            ('id', self.id),
            ('type', self.socket_type),
            ('position', [self.pos().x(), self.pos().y()]),
            ('metadata', metadata)
        ])

    def deserialize(self, data: OrderedDict, hashmap: dict = None):
        self.id = data['id']
        self.socket_type = data['type']
        self.setPos(QPointF(*data['position']))

        self.metadata = dict(data['metadata'])
        self._pen.setColor(QColor(self.metadata['linecolor']))
        self._pen.setWidth(self.metadata['linewidth'])
        self._brush.setColor(QColor(self.metadata['color']))
