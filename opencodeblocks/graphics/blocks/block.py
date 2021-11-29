# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the base OCB Block. """

from typing import TYPE_CHECKING, Optional, OrderedDict, Tuple

import time

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QFocusEvent, QMouseEvent, QPen, QColor, QFont, \
                QPainter, QPainterPath
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsProxyWidget, \
    QGraphicsSceneMouseEvent, QLineEdit, QSplitter, QSplitterHandle, \
    QStyleOptionGraphicsItem, QWidget

from opencodeblocks.core.serializable import Serializable
from opencodeblocks.graphics.socket import OCBSocket
from opencodeblocks.graphics.blocks.blocksizegrip import BlockSizeGrip

if TYPE_CHECKING:
    from opencodeblocks.graphics.scene.scene import OCBScene

BACKGROUND_COLOR = QColor("#E3212121")


class OCBTitle(QLineEdit):
    """ The title of an OCBBlock. Needs to be double clicked to interact """

    def __init__(self, content: str, parent: QWidget = None):
        """ Create a new title for an OCBBlock """
        super().__init__(content, parent)
        self.clickTime = None
        self.setReadOnly(True)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Detect double clicks and single clicks are react accordingly by
        dispatching the event to the parent or the current widget
        """
        if self.clickTime is None or (
                self.isReadOnly() and time.time() - self.clickTime > 0.3):
            self.parent().mousePressEvent(event)
        elif self.isReadOnly():
            self.mouseDoubleClickEvent(event)
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
        self.clickTime = time.time()

    def focusOutEvent(self, event: QFocusEvent):
        """ The title is read-only when focused is lost """
        self.setReadOnly(True)
        self.deselect()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """ Toggle readonly mode when double clicking """
        self.setReadOnly(not self.isReadOnly())
        if not self.isReadOnly():
            self.setFocus(Qt.MouseFocusReason)


class OCBBlock(QGraphicsItem, Serializable):

    """ Base class for blocks in OpenCodeBlocks. """

    def __init__(self, block_type: str = 'base', source: str = '', position: tuple = (0, 0),
                 width: int = 300, height: int = 200, edge_size: float = 10.0,
                 title: str = 'New block', title_color: str = 'white', title_font: str = "Ubuntu",
                 title_size: int = 10, title_padding=4.0, parent: Optional['QGraphicsItem'] = None):
        """ Base class for blocks in OpenCodeBlocks.

        Args:
            block_type: Block type.
            source: Block source text.
            position: Block position in the scene.
            width: Block width.
            height: Block height.
            edge_size: Block edges size.
            title: Block title.
            title_color: Color of the block title.
            title_font: Font of the block title.
            title_size: Size of the block title.
            title_padding: Padding of the block title.
            parent: Parent of the block.

        """
        QGraphicsItem.__init__(self, parent=parent)
        Serializable.__init__(self)

        self.block_type = block_type
        self.source = source
        self.stdout = ""
        self.image = ""
        self.setPos(QPointF(*position))
        self.sockets_in = []
        self.sockets_out = []

        self.title_height = 3.5 * title_size
        self.title_left_offset = 0

        self._pen_outline = QPen(QColor("#7F000000"))
        self._pen_outline_selected = QPen(QColor("#FFFFA637"))
        self._brush_background = QBrush(BACKGROUND_COLOR)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

        self.setAcceptHoverEvents(True)

        self.holder = QGraphicsProxyWidget(self)
        self.root = QWidget()
        self.root.setAttribute(Qt.WA_TranslucentBackground)
        self.root.setGeometry(
            0, 0,
            int(width),
            int(height)
        )

        self.title_widget = OCBTitle(title, self.root)
        self.title_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setTitleGraphics(
            title_color,
            title_font,
            title_size,
            title_padding
        )

        self.splitter = OCBSplitter(self, Qt.Vertical, self.root)

        self.size_grip = BlockSizeGrip(self, self.root)

        if type(self) == OCBBlock:  # DO NOT TRUST codacy !!! type(self) should be used, not isinstance.
            # This has to be called at the end of the constructor of
            # every class inheriting this.
            self.holder.setWidget(self.root)

        self.edge_size = edge_size
        self.min_width = 300
        self.min_height = 100
        self.width = width
        self.height = height

        self.moved = False
        self.metadata = {
            'title_metadata': {
                'color': title_color,
                'font': title_font,
                'size': title_size,
                'padding': title_padding,
            },
        }

    def scene(self) -> 'OCBScene':
        """ Get the current OCBScene containing the block. """
        return super().scene()

    def boundingRect(self) -> QRectF:
        """ Get the the block bounding box. """
        return QRectF(0, 0, self.width, self.height).normalized()

    def setTitleGraphics(self, color: str, font: str,
                         size: int, padding: float):
        """ Set the title graphics.

        Args:
            color: title color.
            font: title font.
            size: title size.
            padding: title padding.

        """
        # self.title_widget.setMargin(int(padding))
        self.title_widget.setStyleSheet(
            f"""
            QLineEdit {{
                color : {color};
                background-color: #E3212121;
                border:none;
                padding: {padding}px;
            }}"""
        )
        self.title_widget.setFont(QFont(font, size))

    def paint(self, painter: QPainter,
              option: QStyleOptionGraphicsItem,  # pylint:disable=unused-argument
              widget: Optional[QWidget] = None):  # pylint:disable=unused-argument
        """ Paint the block. """

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addRoundedRect(0, 0, self.width, self.height,
                                    self.edge_size, self.edge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height,
                                    self.edge_size, self.edge_size)
        painter.setPen(
            self._pen_outline_selected if self.isSelected() else self._pen_outline)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path_outline.simplified())

    def _is_in_resize_area(self, pos: QPointF):
        """ Return True if the given position is in the block resize_area. """
        return self.width - self.edge_size < pos.x() \
            and self.height - self.edge_size < pos.y()

    def get_socket_pos(self, socket: OCBSocket) -> Tuple[float]:
        """ Get a socket position to place them on the block sides. """
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
            y = y_offset + side_lenght * \
                sockets.index(socket) / (len(sockets) - 1)
        return x, y

    def update_sockets(self):
        """ Update the sockets positions. """
        for socket in self.sockets_in + self.sockets_out:
            socket.setPos(*self.get_socket_pos(socket))

    def add_socket(self, socket: OCBSocket):
        """ Add a socket to the block. """
        if socket.socket_type == 'input':
            self.sockets_in.append(socket)
        else:
            self.sockets_out.append(socket)
        self.update_sockets()

    def remove_socket(self, socket: OCBSocket):
        """ Remove a socket from the block. """
        if socket.socket_type == 'input':
            self.sockets_in.remove(socket)
        else:
            self.sockets_out.remove(socket)
        socket.remove()
        self.update_sockets()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """ OCBBlock reaction to a mouseReleaseEvent. """
        if self.moved:
            self.moved = False
            self.scene().history.checkpoint("Moved block", set_modified=True)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        """ OCBBlock reaction to a mouseMoveEvent. """
        super().mouseMoveEvent(event)
        self.moved = True

    def remove(self):
        """ Remove the block from the scene containing it. """
        scene = self.scene()
        for socket in self.sockets_in + self.sockets_out:
            self.remove_socket(socket)
        if scene is not None:
            scene.removeItem(self)

    def update_all(self):
        """ Update sockets and title. """
        self.update_sockets()
        if hasattr(self, 'title_widget'):
            # We make the resizing of splitter only affect
            # the last element of the split view
            sizes = self.splitter.sizes()
            old_height = self.splitter.height()
            self.splitter.setGeometry(
                int(self.edge_size),
                int(self.edge_size + self.title_height),
                int(self.width - self.edge_size * 2),
                int(self.height - self.edge_size * 2 - self.title_height)
            )
            if len(sizes) > 1:
                height_delta = self.splitter.height() - old_height
                sizes[-1] += height_delta
                self.splitter.setSizes(sizes)

            self.title_widget.setGeometry(
                int(self.edge_size + self.title_left_offset),
                int(self.edge_size / 2),
                int(self.width - self.edge_size * 3),
                int(self.title_height)
            )
            self.size_grip.setGeometry(
                int(self.width - self.edge_size * 2),
                int(self.height - self.edge_size * 2),
                int(self.edge_size * 1.7),
                int(self.edge_size * 1.7)
            )

    @property
    def title(self):
        """ Block title. """
        return self.title_widget.text()

    @title.setter
    def title(self, value: str):
        if hasattr(self, 'title_widget'):
            self.title_widget.setText(value)

    @property
    def width(self):
        """ Block width. """
        return self.root.width()

    @width.setter
    def width(self, value: float):
        self.root.setGeometry(0, 0, int(value), self.root.height())
        self.update_all()

    @property
    def height(self):
        """ Block height. """
        return self.root.height()

    @height.setter
    def height(self, value: float):
        self.root.setGeometry(0, 0, self.root.width(), int(value))
        self.update_all()

    def serialize(self) -> OrderedDict:
        metadata = OrderedDict(sorted(self.metadata.items()))
        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('block_type', self.block_type),
            ('source', self.source),
            ('stdout', self.stdout),
            ('image', self.image),
            ('splitter_pos', self.splitter.sizes()),
            ('position', [self.pos().x(), self.pos().y()]),
            ('width', self.width),
            ('height', self.height),
            ('metadata', metadata),
            ('sockets', [socket.serialize()
             for socket in self.sockets_in + self.sockets_out]),
        ])

    def deserialize(self, data: dict, hashmap: dict = None,
                    restore_id=True) -> None:
        if restore_id:
            self.id = data['id']
        for dataname in ('title', 'block_type', 'source', 'stdout',
                         'image', 'width', 'height'):
            setattr(self, dataname, data[dataname])

        self.setPos(QPointF(*data['position']))
        self.metadata = dict(data['metadata'])
        self.setTitleGraphics(**self.metadata['title_metadata'])

        if 'splitter_pos' in data:
            self.splitter.setSizes(data['splitter_pos'])

        for socket_data in data['sockets']:
            socket = OCBSocket(block=self)
            socket.deserialize(socket_data, hashmap, restore_id)
            self.add_socket(socket)
            if hashmap is not None:
                hashmap.update({socket_data['id']: socket})


class OCBSplitterHandle(QSplitterHandle):
    """ A handle for splitters with undoable events """

    def mouseReleaseEvent(self, evt: QMouseEvent):
        """ When releasing the handle, save the state to history """
        scene = self.parent().block.scene()
        if scene is not None:
            scene.history.checkpoint("Resize block", set_modified=True)
        return super().mouseReleaseEvent(evt)


class OCBSplitter(QSplitter):
    """ A spliter with undoable events """

    def __init__(self, block: OCBBlock, orientation: int, parent: QWidget):
        """ Create a new OCBSplitter """
        super().__init__(orientation, parent)
        self.block = block

    def createHandle(self):
        """ Return the middle handle of the splitter """
        return OCBSplitterHandle(self.orientation(), self)
