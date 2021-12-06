# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for OCB Sockets """

from __future__ import annotations
from typing import List, Optional, OrderedDict, TYPE_CHECKING
import math

from PyQt5.QtCore import QPoint, QPointF, QRectF
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygon
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from opencodeblocks.core.serializable import Serializable

if TYPE_CHECKING:
    from opencodeblocks.graphics.edge import OCBEdge
    from opencodeblocks.blocks.block import OCBBlock

DEFAULT_SOCKET_DATA = {
    "type": "input",
    "metadata": {
        "color": "#FF55FFF0",
        "linecolor": "#FF000000",
        "linewidth": 1.0,
        "radius": 6.0,
    },
}
NONE_OPTIONAL_FIELDS = {"position"}


class OCBSocket(QGraphicsItem, Serializable):

    """Base class for sockets in OpenCodeBlocks."""

    def __init__(
        self,
        block: "OCBBlock",
        socket_type: str = "undefined",
        flow_type: str = "exe",
        radius: float = 10.0,
        color: str = "#FF55FFF0",
        linewidth: float = 1.0,
        linecolor: str = "#FF000000",
    ):
        """Base class for sockets in OpenCodeBlocks.

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

        self.edges: List["OCBEdge"] = []
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

    def add_edge(self, edge: "OCBEdge", is_destination: bool):
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

    def remove_edge(self, edge: "OCBEdge"):
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
            angles = [0, 2 * math.pi / 3, -2 * math.pi / 3]
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

    def complete_with_default(self, data: OrderedDict) -> None:
        """Add default data in place when fields are missing"""
        for key in NONE_OPTIONAL_FIELDS:
            if key not in data:
                raise ValueError(f"{key} of the socket is missing")

        for key in DEFAULT_SOCKET_DATA.keys():
            if key not in data:
                data[key] = DEFAULT_SOCKET_DATA[key]

