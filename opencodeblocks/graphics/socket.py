# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for OCB Sockets """

from __future__ import annotations

from typing import Optional
from PyQt5.QtCore import QRectF

from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget


class OCBSocket(QGraphicsItem):

    def __init__(self, block:'OCBBlock', socket_type:str='undefined', index:int=0, radius:float=6.0,
            color:str='#FF55FFF0', linewidth:float=1.0, linecolor:str='#FF000000'):

        self.block = block
        self.edges = []
        self.socket_type = socket_type
        self.index = index
        super().__init__(parent=self.block)

        self.radius = radius
        self._pen = QPen(QColor(linecolor))
        self._pen.setWidth(linewidth)
        self._brush = QBrush(QColor(color))

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
