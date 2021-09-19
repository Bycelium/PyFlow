# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB View """

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QMouseEvent, QPainter, QWheelEvent
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsView

from opencodeblocks.graphics.scene import OCBScene

class OCBView(QGraphicsView):

    """ View for the OCB Window. """

    def __init__(self, scene:OCBScene, parent=None,
            zoom_step:float=1.25, zoom_min:float=0.2, zoom_max:float=5):
        super().__init__(parent=parent)
        self.scene = scene
        self.zoom = 1
        self.zoom_step, self.zoom_min, self.zoom_max = zoom_step, zoom_min, zoom_max

        self.init_ui()
        self.setScene(self.scene)

    def init_ui(self):
        """ Initialize the custom OCB View UI. """
        # Antialiasing
        self.setRenderHints(
            QPainter.Antialiasing |
            QPainter.HighQualityAntialiasing |
            QPainter.TextAntialiasing |
            QPainter.SmoothPixmapTransform
        )
        # Better Update
        self.setViewportUpdateMode(
            QGraphicsView.FullViewportUpdate
        )
        # Remove scroll bars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Zoom on cursor
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def mousePressEvent(self, event: QMouseEvent):
        """Dispatch Qt's mousePress events to corresponding functions below"""
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Dispatch Qt's mouseRelease events to corresponding functions below"""
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event: QMouseEvent):
        """ Drag the scene around on middleMouseButtonPress. """
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event: QMouseEvent):
        """ Release the scene on middleMouseButtonPress. """
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def leftMouseButtonPress(self, event: QMouseEvent):
        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event: QMouseEvent):
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """ Handles zooming with mouse wheel """
        # calculate zoom
        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_step
        else:
            zoom_factor = 1 / self.zoom_step

        if self.zoom_min < self.zoom * zoom_factor < self.zoom_max:
            self.zoom *= zoom_factor
            self.scale(zoom_factor, zoom_factor)

    def getItemAtClick(self, event: QEvent) -> QGraphicsItem:
        """ Return the object on which we've clicked/release mouse button """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj
