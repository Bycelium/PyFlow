# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB Edge. """

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QWidget

from opencodeblocks.graphics.edge import OCBEdge


class OCBCodeEdge(OCBEdge):

    """Base class for directed edges in OpenCodeBlocks."""

    def __init__(
        self,
        edge_running_color: str = "#FF0000",
        edge_transmitting_color: str = "#FFFFA637",
    ):
        super().__init__()
        self.edge_running_color = edge_running_color
        self.edge_transmitting_color = edge_transmitting_color

        self.run_color = 0
        self._pen_outline = QPen(QColor("#7F000000"))
        self._pen_outline_running = QPen(QColor("#FF0000"))
        self._pen_outline_transmitting = QPen(QColor("#FFFFA637"))
        self._pen_outlines = [
            self._pen_outline,
            self._pen_outline_running,
            self._pen_outline_transmitting,
        ]

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint:disable=unused-argument
        widget: Optional[QWidget] = None,
    ):  # pylint:disable=unused-argument
        """Paint the edge."""
        self.update_path()
        painter.setPen(
            self._pen_selected
            if self.isSelected()
            else self._pen_outlines[self.run_color]
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())
