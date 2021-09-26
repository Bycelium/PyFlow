# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB Block visualization """

import typing

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QPen, QColor, QFont, QPainter, QPainterPath
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QStyleOptionGraphicsItem, QWidget

from opencodeblocks.core.node import Node


class OCBBlock(QGraphicsItem):
    def __init__(self, node:Node,
            title_color:str='white', title_font:str="Ubuntu", title_size:int=10, title_padding=4.0,
            title_rel_height=0.12,
            parent: typing.Optional['QGraphicsItem']=None) -> None:
        super().__init__(parent=parent)
        self.node = node

        self.width = 180
        self.height = 240
        self.edge_size = 10.0

        self.title_graphics = self.init_title_graphics(
            title_color, title_font, title_size, title_padding)
        self.title = self.node.title
        self.title_rel_height = title_rel_height
        self.title_height = int(self.title_rel_height * self.height)

        self._pen_outline = QPen(QColor("#7F000000"))
        self._pen_outline_selected = QPen(QColor("#FFFFA637"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self.init_ui()

    def init_ui(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0,
            self.width + 2 * self.edge_size, self.height + 2 * self.edge_size).normalized()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
            widget: typing.Optional[QWidget]=None) -> None:
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height,
            self.edge_size, self.edge_size)
        path_title.addRect(0, self.title_height - self.edge_size,
            self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.title_height - self.edge_size,
            self.edge_size, self.edge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height,
            self.edge_size, self.edge_size)
        path_title.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.title_height,
            self.edge_size, self.edge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_title.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height,
            self.edge_size, self.edge_size)
        painter.setPen(self._pen_outline_selected if self.isSelected() else self._pen_outline)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path_outline.simplified())

    def init_title_graphics(self, color:str, font:str, size:int,
            padding:float) -> QGraphicsTextItem:
        title = QGraphicsTextItem(self)
        title.setDefaultTextColor(QColor(color))
        title.setFont(QFont(font, size))
        title.setPos(padding, 0)
        title.setTextWidth(self.width - 2 * self.edge_size)
        return title

    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, value:str):
        self._title = value
        self.title_graphics.setPlainText(self._title)

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, value:int):
        self._width = value

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, value:int):
        self._height = value
