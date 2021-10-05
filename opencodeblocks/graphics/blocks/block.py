# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the base OCB Block. """

from typing import Optional, OrderedDict, Tuple

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QPen, QColor, QFont, QPainter, QPainterPath
from PyQt5.QtWidgets import QGraphicsItem,QGraphicsSceneMouseEvent, QGraphicsTextItem, \
    QStyleOptionGraphicsItem, QWidget, QApplication

from opencodeblocks.core.serializable import Serializable
from opencodeblocks.graphics.socket import OCBSocket

class OCBBlock(QGraphicsItem, Serializable):
    def __init__(self, title:str='New block', block_type:str='base', source:str='',
            position:tuple=(0, 0), title_color:str='white', title_font:str="Ubuntu",
            title_size:int=10, title_padding=4.0, parent: Optional['QGraphicsItem']=None):
        QGraphicsItem.__init__(self, parent=parent)
        Serializable.__init__(self)

        self.block_type = block_type
        self.source = source
        self.setPos(QPointF(*position))
        self.sockets_in = []
        self.sockets_out = []

        self._min_width = 300
        self._min_height = 100

        self.width = 300
        self.height = 200
        self.edge_size = 10.0

        self.title_height = 3 * title_size
        self.title_graphics = QGraphicsTextItem(self)
        self.setTitleGraphics(title_color, title_font, title_size, title_padding)
        self.title = title

        self._pen_outline = QPen(QColor("#7F000000"))
        self._pen_outline_selected = QPen(QColor("#FFFFA637"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

        self.resizing = False
        self.moved = False
        self.metadata = {
            'title_metadata': {
                'color': title_color,
                'font': title_font,
                'size': title_size,
                'padding': title_padding,
            },
        }

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height).normalized()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
            widget: Optional[QWidget]=None) -> None:
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

    def _is_in_resize_area(self, pos:QPointF):
        return self.width - pos.x() < 2 * self.edge_size \
            and self.height - pos.y() < 2 * self.edge_size

    def get_socket_pos(self, socket:OCBSocket) -> Tuple[float]:
        if socket.socket_type == 'input':
            x = 0
            sockets = self.sockets_in
        else:
            x = self.width
            sockets = self.sockets_out

        y_offset = self.title_height + 2 * socket.radius
        if len(sockets) < 2:
            y = y_offset
        else:
            side_lenght = self.height - y_offset - 2 * socket.radius - self.edge_size
            y = y_offset + side_lenght * sockets.index(socket) / (len(sockets) - 1)
        return x, y

    def update_sockets(self):
        for socket in self.sockets_in + self.sockets_out:
            socket.setPos(*self.get_socket_pos(socket))

    def add_socket(self, socket:OCBSocket):
        if socket.socket_type == 'input':
            self.sockets_in.append(socket)
        else:
            self.sockets_out.append(socket)
        self.update_sockets()

    def remove_socket(self, socket:OCBSocket):
        if socket.socket_type == 'input':
            self.sockets_in.remove(socket)
        else:
            self.sockets_out.remove(socket)
        socket.remove()
        self.update_sockets()

    def mousePressEvent(self, event:QGraphicsSceneMouseEvent):
        pos = event.pos()
        if self._is_in_resize_area(pos) and event.buttons() == Qt.MouseButton.LeftButton:
            self.resize_start = pos
            self.resizing = True
            QApplication.setOverrideCursor(Qt.CursorShape.SizeFDiagCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event:QGraphicsSceneMouseEvent):
        self.resizing = False
        QApplication.restoreOverrideCursor()
        if self.moved:
            self.moved = False
            self.scene().history.checkpoint("Moved block")
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event:QGraphicsSceneMouseEvent):
        if self.resizing:
            delta = event.pos() - self.resize_start
            self.width = max(self.width + delta.x(), self._min_width)
            self.height = max(self.height + delta.y(), self._min_height)
            self.resize_start = event.pos()
            self.title_graphics.setTextWidth(self.width - 2 * self.edge_size)
            self.update()
        else:
            super().mouseMoveEvent(event)
            self.moved = True

    def setTitleGraphics(self, color:str, font:str, size:int, padding:float):
        self.title_graphics.setDefaultTextColor(QColor(color))
        self.title_graphics.setFont(QFont(font, size))
        self.title_graphics.setPos(padding, 0)
        self.title_graphics.setTextWidth(self.width - 2 * self.edge_size)

    def remove(self):
        scene = self.scene()
        for socket in self.sockets_in + self.sockets_out:
            self.remove_socket(socket)
        if scene is not None:
            scene.removeItem(self)

    def update_all(self):
        self.update_sockets()
        if hasattr(self, 'title_graphics'):
            self.title_graphics.setTextWidth(self.width - 2 * self.edge_size)

    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, value:str):
        self._title = value
        if hasattr(self, 'title_graphics'):
            self.title_graphics.setPlainText(self._title)

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, value:float):
        self._width = value
        self.update_all()

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, value:float):
        self._height = value
        self.update_all()

    def serialize(self) -> OrderedDict:
        metadata = OrderedDict(sorted(self.metadata.items()))
        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('block_type', self.block_type),
            ('source', self.source),
            ('position', [self.pos().x(), self.pos().y()]),
            ('width', self.width),
            ('height', self.height),
            ('metadata', metadata),
            ('sockets', [socket.serialize() for socket in self.sockets_in + self.sockets_out]),
        ])

    def deserialize(self, data: dict, hashmap:dict=None) -> None:
        for dataname in ('id', 'title', 'block_type', 'source', 'width', 'height'):
            setattr(self, dataname, data[dataname])
        self.setPos(QPointF(*data['position']))
        self.metadata = dict(data['metadata'])
        self.setTitleGraphics(**self.metadata['title_metadata'])

        for socket_data in data['sockets']:
            socket = OCBSocket(block=self)
            socket.deserialize(socket_data, hashmap)
            self.add_socket(socket)
            hashmap.update({socket_data['id']: socket})
