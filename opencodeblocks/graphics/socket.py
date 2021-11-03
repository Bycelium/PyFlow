# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for OCB Sockets """

from __future__ import annotations
from typing import Optional, OrderedDict, TYPE_CHECKING

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from opencodeblocks.core.serializable import Serializable

if TYPE_CHECKING:
    from opencodeblocks.graphics.edge import OCBEdge
    from opencodeblocks.graphics.blocks.block import OCBBlock


class OCBSocket(QGraphicsItem, Serializable):

    """ Base class for sockets in OpenCodeBlocks. """

    def __init__(self, block:'OCBBlock', socket_type:str='undefined', radius:float=6.0,
            color:str='#FF55FFF0', linewidth:float=1.0, linecolor:str='#FF000000'):
        """ Base class for sockets in OpenCodeBlocks.

        Args:
            block: Block containing the socket.
            socket_type: Type of the socket, one of ('undefined', 'input', 'output').
            radius: Radius of the socket graphics.
            color: Color of the socket graphics.
            linewidth: Linewidth of the socket graphics.
            linecolor: Linecolor of the socket graphics.

        """
        Serializable.__init__(self)
        self.block = block
        QGraphicsItem.__init__(self, parent=self.block)

        self.edges = []
        self.socket_type = socket_type

        self.radius = radius
        self._pen = QPen(QColor(linecolor))
        self._pen.setWidth(int(linewidth))
        self._brush = QBrush(QColor(color))

        self.metadata = {
            'radius': radius,
            'color': color,
            'linewidth': linewidth,
            'linecolor': linecolor,
        }

    def add_edge(self, edge:'OCBEdge'):
        """ Add a given edge to the socket edges. """
        if not self._allow_multiple_edges:
            for prev_edge in self.edges:
                prev_edge.remove()
        self.edges.append(edge)

    def remove_edge(self, edge:'OCBEdge'):
        """ Remove a given edge from the socket edges. """
        self.edges.remove(edge)

    def remove(self):
        """ Remove the socket and all its edges from the scene it is in. """
        for edge in self.edges:
            edge.remove()
        scene = self.scene()
        if scene is not None:
            scene.removeItem(self)

    @property
    def _allow_multiple_edges(self):
        return self.socket_type != 'input'

    def paint(self, painter: QPainter,
            option: QStyleOptionGraphicsItem, #pylint:disable=unused-argument
            widget: Optional[QWidget]=None): #pylint:disable=unused-argument
        """ Paint the socket. """
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        r = self.radius
        painter.drawEllipse(int(-r),int(-r),int(2*r),int(2*r))

    def boundingRect(self) -> QRectF:
        """ Get the socket bounding box. """
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

    def deserialize(self, data: OrderedDict, hashmap: dict = None, restore_id=True):
        if restore_id:
            self.id = data['id']
        self.socket_type = data['type']
        self.setPos(QPointF(*data['position']))

        self.metadata = dict(data['metadata'])
        self._pen.setColor(QColor(self.metadata['linecolor']))
        self._pen.setWidth(int(self.metadata['linewidth']))
        self._brush.setColor(QColor(self.metadata['color']))
