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
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.HighQualityAntialiasing |
            QPainter.RenderHint.TextAntialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        # Better Update
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        # Remove scroll bars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Zoom on cursor
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def mousePressEvent(self, event: QMouseEvent):
        """Dispatch Qt's mousePress events to corresponding functions below"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Dispatch Qt's mouseRelease events to corresponding functions below"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def fake_drag(self, event: QMouseEvent, action="press"):
        """ Drag the scene around. """
        if action == "press":
            releaseEvent = QMouseEvent(QEvent.Type.MouseButtonRelease,
                event.localPos(), event.screenPos(),
                Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, event.modifiers())
            super().mouseReleaseEvent(releaseEvent)
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            return QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                Qt.MouseButton.LeftButton, event.buttons() | Qt.MouseButton.LeftButton,
                event.modifiers())
        return QMouseEvent(event.type(), event.localPos(), event.screenPos(),
            Qt.MouseButton.LeftButton,event.buttons() & ~Qt.MouseButton.LeftButton,
            event.modifiers())

    def middleMouseButtonPress(self, event: QMouseEvent):
        super().mousePressEvent(event)

    def middleMouseButtonRelease(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)

    def leftMouseButtonPress(self, event: QMouseEvent):
        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event: QMouseEvent):
        event = self.fake_drag(event, "press")
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event: QMouseEvent):
        event = self.fake_drag(event, "release")
        super().mouseReleaseEvent(event)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

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

    def getItemAtClick(self, event: QMouseEvent) -> QGraphicsItem:
        """ Return the object on which we've clicked/release mouse button """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj
