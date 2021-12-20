# pylint:disable=unused-argument

from math import floor
import json
from typing import OrderedDict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QMouseEvent, QPaintEvent, QPainter
from PyQt5.QtWidgets import QPushButton, QWidget
from opencodeblocks.blocks.block import OCBBlock


eps = 1


class DrawableWidget(QWidget):
    """A drawable widget is a canvas like widget on which you can doodle"""

    def __init__(self, parent: QWidget):
        """Create a new Drawable widget"""
        super().__init__(parent)
        self.setAttribute(Qt.WA_PaintOnScreen)
        self.pixel_width = 24
        self.pixel_height = 24
        self.color_buffer = []
        self.mouse_down = False
        for _ in range(self.pixel_width):
            self.color_buffer.append([])
            for _ in range(self.pixel_height):
                # color hex encoded as AARRGGBB
                self.color_buffer[-1].append(0xFFFFFFFF)

    def clearDrawing(self):
        """Clear the drawing"""
        for i in range(self.pixel_width):
            for j in range(self.pixel_height):
                self.color_buffer[i][j] = 0xFFFFFFFF

    def paintEvent(self, evt: QPaintEvent):
        """Draw the content of the widget"""
        painter = QPainter(self)

        for i in range(self.pixel_width):
            self.color_buffer.append([])
            for j in range(self.pixel_height):
                w = self.width() / self.pixel_width
                h = self.height() / self.pixel_height
                painter.fillRect(
                    w * i,
                    h * j,
                    w + eps,
                    h + eps,
                    QColor.fromRgb(self.color_buffer[i][j]),
                )

    def mouseMoveEvent(self, evt: QMouseEvent):
        """Change the drawing when dragging the mouse around"""
        if self.mouse_down:
            x = floor(evt.x() / self.width() * self.pixel_width)
            y = floor(evt.y() / self.height() * self.pixel_height)
            if 0 <= x < self.pixel_width and 0 <= y < self.pixel_height:
                self.color_buffer[x][y] = 0xFF000000
                self.repaint()

    def mousePressEvent(self, evt: QMouseEvent):
        """Signal that the drawing starts"""
        self.mouse_down = True

    def mouseReleaseEvent(self, evt: QMouseEvent):
        """Signal that the drawing stops"""
        self.mouse_down = False


class OCBDrawingBlock(OCBBlock):
    """An OCBBlock on which you can draw, to test your CNNs for example"""

    def __init__(self, **kwargs):
        """Create a new OCBBlock"""
        super().__init__(**kwargs)

        self.draw_area = DrawableWidget(self.root)

        self.splitter.addWidget(self.draw_area)  # QGraphicsView
        self.run_button = QPushButton("Clear", self.root)
        self.run_button.move(
            int(self.edge_size * 2),
            int(self.title_widget.height() + self.edge_size * 2),
        )
        self.run_button.setFixedSize(int(8 * self.edge_size), int(3 * self.edge_size))
        self.run_button.clicked.connect(self.draw_area.clearDrawing)
        self.holder.setWidget(self.root)

    @property
    def drawing(self):
        """A json-encoded representation of the drawing"""
        return json.dumps(self.draw_area.color_buffer)

    @drawing.setter
    def drawing(self, value: str):
        self.draw_area.color_buffer = json.loads(value)

    def serialize(self):
        """Return a serialized version of this widget"""
        base_dict = super().serialize()
        base_dict["drawing"] = self.drawing

        return base_dict

    def deserialize(
        self, data: OrderedDict, hashmap: dict = None, restore_id: bool = True
    ):
        """Restore a markdown block from it's serialized state"""
        for dataname in ["drawing"]:
            if dataname in data:
                setattr(self, dataname, data[dataname])

        super().deserialize(data, hashmap, restore_id)
