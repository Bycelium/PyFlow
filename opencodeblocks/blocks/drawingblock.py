from math import floor

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QMouseEvent, QPaintEvent, QPainter, QPen
from PyQt5.QtWidgets import QPushButton, QWidget
from opencodeblocks.blocks.block import OCBBlock


eps = 1

class DrawableWidget(QWidget):
    def __init__(self, parent: QWidget):
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
        for i in range(self.pixel_width):
            for j in range(self.pixel_height):
                 self.color_buffer[i][j] = 0xFFFFFFFF

    def paintEvent(self, evt: QPaintEvent):
        painter = QPainter(self)
        
        for i in range(self.pixel_width):
            self.color_buffer.append([])
            for j in range(self.pixel_height):
                w = self.width() / self.pixel_width
                h = self.height() / self.pixel_height
                painter.fillRect(w*i,h*j,w + eps,h + eps,QColor.fromRgb(self.color_buffer[i][j]))

    def mouseMoveEvent(self, evt: QMouseEvent):
        if self.mouse_down:
            x = floor(evt.x() / self.width() * self.pixel_width)
            y = floor(evt.y() / self.height() * self.pixel_height)
            if 0 <= x < self.pixel_width and 0 <= y < self.pixel_height:
                self.color_buffer[x][y] = 0xFF000000
                self.repaint()

    def mousePressEvent(self, evt: QMouseEvent):
            self.mouse_down = True

    def mouseReleaseEvent(self, evt: QMouseEvent):
            self.mouse_down = False

class OCBDrawingBlock(OCBBlock):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.draw_area = DrawableWidget(self.root)

        self.splitter.addWidget(self.draw_area) # QGraphicsView
        self.run_button = QPushButton("Clear", self.root)
        self.run_button.move(int(self.edge_size * 2), int(self.title_widget.height() + self.edge_size * 2))
        self.run_button.setFixedSize(int(8 * self.edge_size),int(3 * self.edge_size))
        self.run_button.clicked.connect(self.draw_area.clearDrawing)
        self.holder.setWidget(self.root)

