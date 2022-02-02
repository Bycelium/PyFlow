# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>
# pylint:disable=unused-argument

""" Module for the Drawing Block.

A block in which you can draw.

"""

from math import floor
import json
from typing import OrderedDict

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QMouseEvent, QPaintEvent, QPainter
from PyQt5.QtWidgets import QPushButton, QWidget
from pyflow.blocks.executableblock import ExecutableBlock


eps = 1


class DrawableWidget(QWidget):
    """A drawable widget is a canvas like widget on which you can doodle."""

    on_value_changed = pyqtSignal()

    def __init__(self, parent: QWidget):
        """Create a new Drawable widget."""
        super().__init__(parent)
        self.setAttribute(Qt.WA_PaintOnScreen)
        self.pixel_width = 24
        self.pixel_height = 24
        self.color_buffer = []
        self.mouse_down = False
        for _ in range(self.pixel_width):
            self.color_buffer.append([])
            for _ in range(self.pixel_height):
                # 0 = white, 1 = black
                self.color_buffer[-1].append(0)

    def clearDrawing(self):
        """Clear the drawing."""
        for i in range(self.pixel_width):
            for j in range(self.pixel_height):
                self.color_buffer[i][j] = 0

    def paintEvent(self, evt: QPaintEvent):
        """Draw the content of the widget."""
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
                    # hex color encoded as AARRGGBB
                    QColor.fromRgb(
                        0xFF000000 if self.color_buffer[i][j] else 0xFFFFFFFF
                    ),
                )

    def mouseMoveEvent(self, evt: QMouseEvent):
        """Change the drawing when dragging the mouse around."""
        if self.mouse_down:
            x = floor(evt.x() / self.width() * self.pixel_width)
            y = floor(evt.y() / self.height() * self.pixel_height)
            if 0 <= x < self.pixel_width and 0 <= y < self.pixel_height:
                self.color_buffer[x][y] = 1
                self.repaint()
                self.on_value_changed.emit()

    def mousePressEvent(self, evt: QMouseEvent):
        """Signal that the drawing starts."""
        self.mouse_down = True

    def mouseReleaseEvent(self, evt: QMouseEvent):
        """Signal that the drawing stops."""
        self.mouse_down = False


class DrawingBlock(ExecutableBlock):

    """An Block on which you can draw, to test your CNNs for example."""

    def __init__(self, **kwargs):
        """Create a new Block."""
        super().__init__(block_type="DrawingBlock", **kwargs)

        self.draw_area = DrawableWidget(self.root)
        self.draw_area.on_value_changed.connect(self.valueChanged)
        self.var_name = "drawing"

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
        """A json-encoded representation of the drawing."""
        return json.dumps(self.draw_area.color_buffer)

    @drawing.setter
    def drawing(self, value: str):
        self.draw_area.color_buffer = json.loads(value)

    def serialize(self):
        """Return a serialized version of this widget."""
        base_dict = super().serialize()
        base_dict["drawing"] = self.drawing

        return base_dict

    def valueChanged(self):
        """Called when the content of the drawing block changes."""
        # Make sure that the slider is initialized before trying to run it.
        if self.scene() is not None:
            self.run_right()

    @property
    def source(self):
        """The "source code" of the drawingblock i.e an assignement to the drawing buffer."""
        python_code = f"{self.var_name} = {repr(self.draw_area.color_buffer)}"
        return python_code

    @source.setter
    def source(self, value: str):
        raise RuntimeError("The source of a drawingblock is read-only.")

    def deserialize(
        self, data: OrderedDict, hashmap: dict = None, restore_id: bool = True
    ):
        """Restore a markdown block from it's serialized state."""
        for dataname in ["drawing"]:
            if dataname in data:
                setattr(self, dataname, data[dataname])

        super().deserialize(data, hashmap, restore_id)
