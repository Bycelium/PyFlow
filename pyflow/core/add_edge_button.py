# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the button to add an edge."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List, Optional

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

if TYPE_CHECKING:
    from pyflow.blocks.executableblock import ExecutableBlock
    from pyflow.core.edge import Edge


class AddEdgeButton(QGraphicsItem):

    """Base class for the button to add an edge."""

    def __init__(
        self,
        block: "ExecutableBlock",
    ):
        """Base class for the button to add an edge."""

        self.block = block
        QGraphicsItem.__init__(self, parent=self.block)

        self.edges: List["Edge"] = []

        self.radius = 6
        self._pen = QPen(QColor("#FF000000"))
        self._pen.setWidth(int(1))
        self._brush = QBrush(QColor("#FF55FFF0"))

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint:disable=unused-argument
        widget: Optional[QWidget] = None,  # pylint:disable=unused-argument
    ):
        """Paint the button."""
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        r = self.radius
        painter.drawEllipse(int(-r), int(-r), int(2 * r), int(2 * r))

    def boundingRect(self) -> QRectF:
        """Get the button bounding box."""
        r = self.radius
        return QRectF(-r, -r, 2 * r, 2 * r)
