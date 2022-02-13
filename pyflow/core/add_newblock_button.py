# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the button to create a linked block."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from PyQt5.QtCore import QRectF, QPoint
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygon
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QGraphicsSceneHoverEvent
    from pyflow.blocks.executableblock import ExecutableBlock
    from pyflow.core.edge import Edge


class AddNewBlockButton(QGraphicsItem):

    """Base class for the button to create a new linked block."""

    def __init__(
        self,
        block: "ExecutableBlock",
    ):
        """Base class for the button to create a new linked block."""

        self.block = block
        QGraphicsItem.__init__(self, parent=self.block)

        self.edges: List["Edge"] = []

        self.radius = 9

        self._pen = QPen(QColor("#44000000"))
        self._pen.setWidth(int(1))

        self._normal_brush = QBrush(QColor("#1155FFF0"))
        self._hover_brush = QBrush(QColor("#FF23E9D8"))
        self._block_hover_brush = QBrush(QColor("#8855FFF0"))
        self._brush = self._normal_brush

        self.setAcceptHoverEvents(True)

    def set_highlight(self, value: bool) -> None:
        if value:
            self._brush = self._block_hover_brush
        else:
            self._brush = self._normal_brush

    def hoverEnterEvent(self, event: "QGraphicsSceneHoverEvent") -> None:
        """Handle the event when the mouse enters the button."""
        self._brush = self._hover_brush
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: "QGraphicsSceneHoverEvent") -> None:
        """Handle the event when the mouse leaves the button."""
        self._brush = self._normal_brush
        return super().hoverLeaveEvent(event)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint:disable=unused-argument
        widget: Optional[QWidget] = None,  # pylint:disable=unused-argument
    ):
        """Paint the button."""
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        polygon = QPolygon()
        polygon.append(QPoint(-self.radius, -self.radius))
        polygon.append(QPoint(self.radius, -self.radius))
        polygon.append(QPoint(self.radius, self.radius))
        polygon.append(QPoint(-self.radius, self.radius))
        painter.drawPolygon(polygon)

    def boundingRect(self) -> QRectF:
        """Get the button bounding box."""
        r = self.radius
        return QRectF(-r, -r, 2 * r, 2 * r)
