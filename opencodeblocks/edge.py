# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB Edge. """

from typing import Optional, OrderedDict

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsPathItem, QStyleOptionGraphicsItem, QWidget

from opencodeblocks.serializable import Serializable
from opencodeblocks.socket import OCBSocket


class OCBEdge(QGraphicsPathItem, Serializable):

    """Base class for directed edges in OpenCodeBlocks."""

    def __init__(
        self,
        edge_width: float = 4.0,
        path_type="bezier",
        edge_color="#001000",
        edge_selected_color="#00ff00",
        source: QPointF = QPointF(0, 0),
        destination: QPointF = QPointF(0, 0),
        source_socket: OCBSocket = None,
        destination_socket: OCBSocket = None,
    ):
        """Base class for edges in OpenCodeBlocks.

        Args:
            edge_width: Width of the edge.
            path_type: Type of path, one of ('direct', 'bezier').
            edge_color: Color of the edge.
            edge_selected_color: Color of the edge when it is selected.
            source: Source point of the directed edge.
            destination: Destination point of the directed edge.
            source_socket: Source socket of the directed edge, overrides source.
            destination_socket: Destination socket of the directed edge, overrides destination.

        """

        Serializable.__init__(self)
        QGraphicsPathItem.__init__(self, parent=None)
        self._pen = QPen(QColor(edge_color))
        self._pen.setWidthF(edge_width)

        self._pen_dragging = QPen(QColor(edge_color))
        self._pen_dragging.setWidthF(edge_width)
        self._pen_dragging.setStyle(Qt.PenStyle.DashLine)

        self._pen_selected = QPen(QColor(edge_selected_color))
        self._pen_selected.setWidthF(edge_width)

        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(-1)

        self.path_type = path_type

        self.source_socket = source_socket
        self.destination_socket = destination_socket

        self._source = source
        self._destination = destination
        self.update_path()

    def remove_from_socket(self, socket_type="source"):
        """Remove the edge from the sockets it is snaped to on the given socket_type.

        Args:
            socket_type: One of ('source', 'destination').

        """
        socket_name = f"{socket_type}_socket"
        socket = getattr(self, socket_name, OCBSocket)
        if socket is not None:
            socket.remove_edge(self)
            setattr(self, socket_name, None)

    def remove_from_sockets(self):
        """Remove the edge from all sockets it is snaped to."""
        self.remove_from_socket("source")
        self.remove_from_socket("destination")

    def remove(self):
        """Remove the edge from the scene in which it is drawn."""
        scene = self.scene()
        if scene is not None:
            self.remove_from_sockets()
            scene.removeItem(self)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint:disable=unused-argument
        widget: Optional[QWidget] = None,
    ):  # pylint:disable=unused-argument
        """Paint the edge."""
        self.update_path()
        pen = self._pen_dragging if self.destination_socket is None else self._pen
        painter.setPen(self._pen_selected if self.isSelected() else pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())

    def update_path(self):
        """Update the edge path depending on the path_type."""
        path = QPainterPath(self.source)
        if self.path_type == "direct":
            path.lineTo(self.destination)
        elif self.path_type == "bezier":
            sx, sy = self.source.x(), self.source.y()
            dx, dy = self.destination.x(), self.destination.y()
            mid_dist = (dx - sx) / 2
            path.cubicTo(sx + mid_dist, sy, dx - mid_dist, dy, dx, dy)
        else:
            raise NotImplementedError(f"Unknowed path type: {self.path_type}")
        self.setPath(path)

    @property
    def source(self) -> QPointF:
        """Source point of the directed edge."""
        if self.source_socket is not None:
            return self.source_socket.scenePos()
        return self._source

    @source.setter
    def source(self, value: QPointF):
        self._source = value
        try:
            self.update_path()
        except AttributeError:
            pass

    @property
    def source_socket(self) -> OCBSocket:
        """Source socket of the directed edge."""
        return self._source_socket

    @source_socket.setter
    def source_socket(self, value: OCBSocket):
        self._source_socket = value
        if value is not None:
            self.source_socket.add_edge(self, is_destination=False)
            self.source = value.scenePos()

    @property
    def destination(self) -> QPointF:
        """Destination point of the directed edge."""
        if self.destination_socket is not None:
            return self.destination_socket.scenePos()
        return self._destination

    @destination.setter
    def destination(self, value: QPointF):
        self._destination = value
        try:
            self.update_path()
        except AttributeError:
            pass

    @property
    def destination_socket(self) -> OCBSocket:
        """Destination socket of the directed edge."""
        return self._destination_socket

    @destination_socket.setter
    def destination_socket(self, value: OCBSocket):
        self._destination_socket = value
        if value is not None:
            self.destination_socket.add_edge(self, is_destination=True)
            self.destination = value.scenePos()

    def serialize(self) -> OrderedDict:
        return OrderedDict(
            [
                ("id", self.id),
                ("path_type", self.path_type),
                (
                    "source",
                    OrderedDict(
                        [
                            (
                                "block",
                                self.source_socket.block.id
                                if self.source_socket
                                else None,
                            ),
                            (
                                "socket",
                                self.source_socket.id if self.source_socket else None,
                            ),
                        ]
                    ),
                ),
                (
                    "destination",
                    OrderedDict(
                        [
                            (
                                "block",
                                self.destination_socket.block.id
                                if self.destination_socket
                                else None,
                            ),
                            (
                                "socket",
                                self.destination_socket.id
                                if self.destination_socket
                                else None,
                            ),
                        ]
                    ),
                ),
            ]
        )

    def deserialize(self, data: OrderedDict, hashmap: dict = None, restore_id=True):
        if restore_id:
            self.id = data["id"]
        self.path_type = data["path_type"]
        try:
            self.source_socket = hashmap[data["source"]["socket"]]
            self.source_socket.add_edge(self, is_destination=False)

            self.destination_socket = hashmap[data["destination"]["socket"]]
            self.destination_socket.add_edge(self, is_destination=True)
            self.update_path()
        except KeyError:
            self.remove()
