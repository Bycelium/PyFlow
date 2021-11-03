# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB View """

from PyQt5.QtCore import QEvent, QPointF, Qt
from PyQt5.QtGui import QMouseEvent, QPainter, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.sip import isdeleted

from opencodeblocks.graphics.scene import OCBScene
from opencodeblocks.graphics.socket import OCBSocket
from opencodeblocks.graphics.edge import OCBEdge
from opencodeblocks.graphics.blocks import OCBBlock

MODE_NOOP = 0
MODE_EDGE_DRAG = 1
MODE_EDITING = 2

MODES = {
    'MODE_NOOP': MODE_NOOP,
    'MODE_EDGE_DRAG': MODE_EDGE_DRAG,
    'MODE_EDITING': MODE_EDITING,
}


class OCBView(QGraphicsView):

    """ View for the OCB Window. """

    def __init__(self, scene:OCBScene, parent=None,
            zoom_step:float=1.25, zoom_min:float=0.2, zoom_max:float=5):
        super().__init__(parent=parent)
        self.mode = MODE_NOOP
        self.zoom = 1
        self.zoom_step, self.zoom_min, self.zoom_max = zoom_step, zoom_min, zoom_max

        self.edge_drag = None
        self.lastMousePos = QPointF(0, 0)
        self.currentSelectedBlock = None

        self.init_ui()
        self.setScene(scene)

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
        # Selection box
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def scene(self) -> OCBScene:
        """ Get current OCBScene. """
        return super().scene()

    def mousePressEvent(self, event: QMouseEvent):
        """ Dispatch Qt's mousePress events to corresponding functions below. """
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

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """ OCBView reaction to mouseMoveEvent. """
        self.lastMousePos = self.mapToScene(event.pos())
        self.drag_edge(event, 'move')
        if event is not None:
            super().mouseMoveEvent(event)

    def middleMouseButtonPress(self, event: QMouseEvent):
        """ OCBView reaction to middleMouseButtonPress event. """
        super().mousePressEvent(event)

    def middleMouseButtonRelease(self, event: QMouseEvent):
        """ OCBView reaction to middleMouseButtonRelease event. """
        super().mouseReleaseEvent(event)

    def leftMouseButtonPress(self, event: QMouseEvent):
        """ OCBView reaction to leftMouseButtonPress event. """
        # If clicked on a block, bring it forward.
        item_at_click = self.itemAt(event.pos())
        if item_at_click is not None:
            while item_at_click.parentItem() is not None:
                if isinstance(item_at_click,OCBBlock):
                    break
                item_at_click = item_at_click.parentItem()

            if isinstance(item_at_click, OCBBlock):
                self.bring_block_forward(item_at_click)

        # If clicked on a socket, start dragging an edge.
        event = self.drag_edge(event, 'press')
        if event is not None:
            super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event: QMouseEvent):
        """ OCBView reaction to leftMouseButtonRelease event. """
        event = self.drag_edge(event, 'release')
        if event is not None:
            super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event: QMouseEvent):
        """ OCBView reaction to rightMouseButtonPress event. """
        event = self.drag_scene(event, "press")
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event: QMouseEvent):
        """ OCBView reaction to rightMouseButtonRelease event. """
        event = self.drag_scene(event, "release")
        super().mouseReleaseEvent(event)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def wheelEvent(self, event: QWheelEvent):
        """ Handles zooming with mouse wheel events. """
        if Qt.Modifier.CTRL == int(event.modifiers()):
            # calculate zoom
            if event.angleDelta().y() > 0:
                zoom_factor = self.zoom_step
            else:
                zoom_factor = 1 / self.zoom_step

            if self.zoom_min < self.zoom * zoom_factor < self.zoom_max:
                self.zoom *= zoom_factor
                self.scale(zoom_factor, zoom_factor)
        else:
            super().wheelEvent(event)

    def deleteSelected(self):
        """ Delete selected items from the current scene. """
        scene = self.scene()
        for selected_item in scene.selectedItems():
            selected_item.remove()
        scene.history.checkpoint("Delete selected elements", set_modified=True)

    def bring_block_forward(self, block: OCBBlock):
        """ Move the selected block in front of other blocks.

        Args:
            block: Block to bring forward.

        """
        if self.currentSelectedBlock is not None and not isdeleted(self.currentSelectedBlock):
            self.currentSelectedBlock.setZValue(0)
        block.setZValue(1)
        self.currentSelectedBlock = block

    def drag_scene(self, event: QMouseEvent, action="press"):
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

    def drag_edge(self, event: QMouseEvent, action="press"):
        """ Create an edge by drag and drop. """
        item_at_click = self.itemAt(event.pos())
        scene = self.scene()
        if action == "press":
            if isinstance(item_at_click, OCBSocket) \
                    and self.mode != MODE_EDGE_DRAG\
                    and item_at_click.socket_type != 'input':
                self.mode = MODE_EDGE_DRAG
                self.edge_drag = OCBEdge(
                    source_socket=item_at_click,
                    destination=self.mapToScene(event.pos())
                )
                scene.addItem(self.edge_drag)
                return
        elif action == "release":
            if self.mode == MODE_EDGE_DRAG:
                if isinstance(item_at_click, OCBSocket) \
                        and item_at_click is not self.edge_drag.source_socket \
                        and item_at_click.socket_type != 'output':
                    self.edge_drag.destination_socket = item_at_click
                    scene.history.checkpoint("Created edge by dragging", set_modified=True)
                else:
                    self.edge_drag.remove()
                self.edge_drag = None
                self.mode = MODE_NOOP
        elif action == "move":
            if self.mode == MODE_EDGE_DRAG:
                self.edge_drag.destination = self.mapToScene(event.pos())
        return event

    def set_mode(self, mode:str):
        """ Change the view mode.

        Args:
            mode: Mode key to change to, must in present in knowed MODES.

        """
        self.mode = MODES[mode]

    def is_mode(self, mode:str):
        """ Return True if the view is in the given mode.

        Args:
            mode: Mode key to compare to, must in present in knowed MODES.

        """
        return self.mode == MODES[mode]
