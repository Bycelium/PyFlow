# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for base Sockets."""

from __future__ import annotations
from typing import List, Optional, OrderedDict, TYPE_CHECKING
import math

from PyQt5.QtCore import QPoint, QPointF, QRectF
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygon
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from pyflow.core.serializable import Serializable

if TYPE_CHECKING:
    from pyflow.core.edge import Edge
    from pyflow.blocks.block import Block


class Socket(QGraphicsItem, Serializable):

    """Base class for sockets in Pyflow."""

    DEFAULT_DATA = {
        "type": "undefined",
        "metadata": {
            "color": "#FF55FFF0",
            "linecolor": "#FF000000",
            "linewidth": 1.0,
            "radius": 6.0,
        },
    }
    MANDATORY_FIELDS = {"position"}

    def __init__(
        self,
        block: "Block",
        socket_type: str = DEFAULT_DATA["type"],
        flow_type: str = "exe",
        radius: float = DEFAULT_DATA["metadata"]["radius"],
        color: str = DEFAULT_DATA["metadata"]["color"],
        linewidth: float = DEFAULT_DATA["metadata"]["linewidth"],
        linecolor: str = DEFAULT_DATA["metadata"]["linecolor"],
    ):
        """Base class for sockets in Pyflow.

        Args:
            block: Block containing the socket.
            socket_type: Type of the socket, one of ('undefined', 'input', 'output').
            flow_type: Type of flow that the socket is linked to, one of ('exe', 'var').
            radius: Radius of the socket graphics.
            color: Color of the socket graphics.
            linewidth: Linewidth of the socket graphics.
            linecolor: Linecolor of the socket graphics.

        """
        Serializable.__init__(self)
        self.block = block
        QGraphicsItem.__init__(self, parent=self.block)

        self.edges: List["Edge"] = []
        self.socket_type = socket_type
        self.flow_type = flow_type

        self.radius = radius
        self._pen = QPen(QColor(linecolor))
        self._pen.setWidth(int(linewidth))
        self._brush = QBrush(QColor(color))

        self.metadata = {
            "radius": radius,
            "color": color,
            "linewidth": linewidth,
            "linecolor": linecolor,
        }

    def add_edge(self, edge: "Edge", is_destination: bool):
        """Add a given edge to the socket edges."""
        if not self._allow_multiple_edges:
            for prev_edge in self.edges:
                prev_edge.remove()
        if self.flow_type == "exe":
            if (is_destination and self.socket_type != "input") or (
                not is_destination and self.socket_type != "output"
            ):
                edge.remove()
                return
        self.edges.append(edge)

    def remove_edge(self, edge: "Edge"):
        """Remove a given edge from the socket edges."""
        self.edges.remove(edge)

    def remove(self):
        """Remove the socket and all its edges from the scene it is in."""
        for edge in self.edges:
            edge.remove()
        scene = self.scene()
        if scene is not None:
            scene.removeItem(self)
        self.setParentItem(None)

    @property
    def _allow_multiple_edges(self):
        if self.flow_type == "exe":
            return True
        raise NotImplementedError

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint:disable=unused-argument
        widget: Optional[QWidget] = None,
    ):  # pylint:disable=unused-argument
        """Paint the socket."""
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        r = self.radius
        if self.flow_type == "exe":
            angles = [-math.pi / 6, -5 * math.pi / 6, math.pi / 2]
            right_triangle_points = [
                QPoint(int(r * math.cos(angle)), int(r * math.sin(angle)))
                for angle in angles
            ]
            painter.drawPolygon(QPolygon(right_triangle_points))
        else:
            painter.drawEllipse(int(-r), int(-r), int(2 * r), int(2 * r))

    def boundingRect(self) -> QRectF:
        """Get the socket bounding box."""
        r = self.radius
        return QRectF(-r, -r, 2 * r, 2 * r)

    def serialize(self) -> OrderedDict:
        metadata = OrderedDict(sorted(self.metadata.items()))
        return OrderedDict(
            [
                ("id", self.id),
                ("type", self.socket_type),
                ("position", [self.pos().x(), self.pos().y()]),
                ("metadata", metadata),
            ]
        )

    def deserialize(self, data: OrderedDict, hashmap: dict = None, restore_id=True):
        if restore_id and "id" in data:
            self.id = data["id"]

        self.complete_with_default(data)

        self.socket_type = data["type"]
        self.setPos(QPointF(*data["position"]))

        self.metadata = dict(data["metadata"])
        self._pen.setColor(QColor(self.metadata["linecolor"]))
        self._pen.setWidth(int(self.metadata["linewidth"]))
        self._brush.setColor(QColor(self.metadata["color"]))
