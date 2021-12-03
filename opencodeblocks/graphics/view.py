# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB View """

import json
import os
from typing import List, Tuple

from PyQt5.QtCore import QEvent, QPointF, Qt
from PyQt5.QtGui import QKeyEvent, QMouseEvent, QPainter, QWheelEvent, QContextMenuEvent
from PyQt5.QtWidgets import QGraphicsView, QMenu
from PyQt5.sip import isdeleted


from opencodeblocks.scene import OCBScene
from opencodeblocks.graphics.socket import OCBSocket
from opencodeblocks.graphics.edge import OCBEdge
from opencodeblocks.blocks import OCBBlock

EPS: float = 1e-10  # To check if blocks are of size 0


class OCBView(QGraphicsView):

    """View for the OCB Window."""

    MODE_NOOP = 0
    MODE_EDGE_DRAG = 1
    MODE_EDITING = 2

    MODES = {
        "NOOP": MODE_NOOP,
        "EDGE_DRAG": MODE_EDGE_DRAG,
        "EDITING": MODE_EDITING,
    }

    def __init__(
        self,
        scene: OCBScene,
        parent=None,
        zoom_step: float = 1.25,
        zoom_min: float = 0.2,
        zoom_max: float = 5,
    ):
        super().__init__(parent=parent)
        self.mode = self.MODE_NOOP
        self.zoom = 1
        self.zoom_step, self.zoom_min, self.zoom_max = zoom_step, zoom_min, zoom_max

        self.edge_drag = None
        self.lastMousePos = QPointF(0, 0)
        self.currentSelectedBlock = None

        self.init_ui()
        self.setScene(scene)

    def init_ui(self):
        """Initialize the custom OCB View UI."""
        # Antialiasing
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.HighQualityAntialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        # Better Update
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        # Remove scroll bars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Zoom on cursor
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        # Selection box
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def scene(self) -> OCBScene:
        """Get current OCBScene."""
        return super().scene()

    def mousePressEvent(self, event: QMouseEvent):
        """Dispatch Qt's mousePress events to corresponding functions below."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Dispatch Qt's mouseRelease events to corresponding functions below"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """OCBView reaction to mouseMoveEvent."""
        self.lastMousePos = self.mapToScene(event.pos())
        self.drag_edge(event, "move")
        if event is not None:
            super().mouseMoveEvent(event)

    def leftMouseButtonPress(self, event: QMouseEvent):
        """OCBView reaction to leftMouseButtonPress event."""
        # If clicked on a block, bring it forward.
        item_at_click = self.itemAt(event.pos())
        if item_at_click is not None:
            while item_at_click.parentItem() is not None:
                if isinstance(item_at_click, OCBBlock):
                    break
                item_at_click = item_at_click.parentItem()

            if isinstance(item_at_click, OCBBlock):
                self.bring_block_forward(item_at_click)

        # If clicked on a socket, start dragging an edge.
        event = self.drag_edge(event, "press")
        if event is not None:
            super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event: QMouseEvent):
        """OCBView reaction to leftMouseButtonRelease event."""
        event = self.drag_edge(event, "release")
        if event is not None:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event: QMouseEvent):
        """OCBView reaction to middleMouseButtonPress event."""
        if self.itemAt(event.pos()) is None:
            event = self.drag_scene(event, "press")
        super().mousePressEvent(event)

    def middleMouseButtonRelease(self, event: QMouseEvent):
        """OCBView reaction to middleMouseButtonRelease event."""
        event = self.drag_scene(event, "release")
        super().mouseReleaseEvent(event)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def centerView(self, x: float, y: float):
        """Move the view so that the position (x,y) is centered."""
        hsb = self.horizontalScrollBar()
        vsb = self.verticalScrollBar()
        hsb.setValue(x * self.zoom - self.width() / 2)
        vsb.setValue(y * self.zoom - self.height() / 2)

    def moveToGlobalView(self) -> bool:
        """
        OCBView reaction to the space bar being pressed.

        Ajust zoom and position to make the whole graph visible.
        If items are selected, then make all the selected items visible instead

        Returns True if the event was handled.
        """

        # The focusItem has priority for this event
        if self.scene().focusItem() is not None:
            return False

        items = self.scene().items()

        # If items are selected, overwride the behvaior
        if len(self.scene().selectedItems()) > 0:
            items = self.scene().selectedItems()

        code_blocks: List[OCBBlock] = [i for i in items if isinstance(i, OCBBlock)]

        if len(code_blocks) == 0:
            return False

        # Get the blocks with min and max x and y coordinates

        min_x: float = min(block.x() for block in code_blocks)
        min_y: float = min(block.y() for block in code_blocks)
        max_x: float = max(block.x() + block.width for block in code_blocks)
        max_y: float = max(block.y() + block.height for block in code_blocks)

        center_x: float = (min_x + max_x) / 2
        center_y: float = (min_y + max_y) / 2

        # Determines the required zoom level

        if max_x - min_x < EPS or max_y - min_y < EPS:
            # Handle the case where there is no block
            return False

        required_zoom_x: float = self.width() / (max_x - min_x)
        required_zoom_y: float = self.height() / (max_y - min_y)

        # Operate the zoom and the translation
        self.setZoom(min(required_zoom_x, required_zoom_y))
        self.centerView(center_x, center_y)
        return True

    def getDistanceToCenter(self, x: float, y: float) -> Tuple[float]:
        """Return the vector from the (x,y) position given to the center of the view"""
        ypos = self.verticalScrollBar().value()
        xpos = self.horizontalScrollBar().value()
        return (
            xpos - x * self.zoom + self.width() / 2,
            ypos - y * self.zoom + self.height() / 2,
        )

    def moveViewOnArrow(self, event: QKeyEvent) -> bool:
        """
        OCBView reaction to an arrow key being pressed.
        Returns True if the event was handled.
        """
        # The focusItem has priority for this event
        if self.scene().focusItem() is not None:
            return False
        if len(self.scene().selectedItems()) > 0:
            return False

        key_id = event.key()
        items = self.scene().items()
        code_blocks = [i for i in items if isinstance(i, OCBBlock)]

        # Pick the block with the center distance (x,y) such that:
        # ||(x,y)|| is minimal but not too close to 0, where ||.|| is the infinity norm
        # This norm was choosen because the movements it generates feel natural.
        # x or y has the correct sign (depends on the key pressed)

        dist_array = []
        for block in code_blocks:
            block_center_x = block.x() + block.width / 2
            block_center_y = block.y() + block.height / 2
            xdist, ydist = self.getDistanceToCenter(block_center_x, block_center_y)
            dist_array.append(
                (
                    block_center_x,
                    block_center_y,
                    xdist,
                    ydist,
                    max(abs(xdist), abs(ydist)),
                )
            )

        if key_id == Qt.Key.Key_Up:
            dist_array = filter(lambda pos: pos[3] > 1, dist_array)
        if key_id == Qt.Key.Key_Down:
            dist_array = filter(lambda pos: pos[3] < -1, dist_array)
        if key_id == Qt.Key.Key_Right:
            dist_array = filter(lambda pos: pos[2] < -1, dist_array)
        if key_id == Qt.Key.Key_Left:
            dist_array = filter(lambda pos: pos[2] > 1, dist_array)
        dist_array = list(dist_array)

        if len(dist_array) <= 0:
            return False
        dist_array.sort(key=lambda d: d[4])

        block_center_x, block_center_y, _, _, _ = dist_array[0]

        self.centerView(block_center_x, block_center_y)
        return True

    def keyPressEvent(self, event: QKeyEvent):
        """OCBView reaction to a key being pressed"""
        key_id = event.key()
        if key_id in [
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
            Qt.Key.Key_Left,
            Qt.Key.Key_Right,
        ]:
            if self.moveViewOnArrow(event):
                return

        super().keyPressEvent(event)

    def retreiveBlockTypes(self) -> List[Tuple[str]]:
        """Retreive the list of stored blocks."""
        block_type_files = os.listdir("blocks")
        block_types = []
        for b in block_type_files:
            filepath = os.path.join("blocks", b)
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.loads(file.read())
                title = "New Block"
                if "title" in data:
                    title = f"New {data['title']} Block"
                    if data["title"] == "Empty":
                        block_types[:0] = [(filepath, title)]
                    else:
                        block_types.append((filepath, title))
        return block_types

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Displays the context menu when inside a view"""
        menu = QMenu(self)
        actionPool = []
        for filepath, block_name in self.retreiveBlockTypes():
            actionPool.append((filepath, menu.addAction(block_name)))

        selectedAction = menu.exec_(self.mapToGlobal(event.pos()))
        for filepath, action in actionPool:
            if action == selectedAction:
                p = self.mapToScene(event.pos())
                self.scene().create_block_from_file(filepath, p.x(), p.y())

    def wheelEvent(self, event: QWheelEvent):
        """Handles zooming with mouse wheel events."""
        if Qt.Modifier.CTRL == int(event.modifiers()):
            # calculate zoom
            if event.angleDelta().y() > 0:
                zoom_factor = self.zoom_step
            else:
                zoom_factor = 1 / self.zoom_step

            new_zoom = self.zoom * zoom_factor
            if self.zoom_min < new_zoom < self.zoom_max:
                self.setZoom(new_zoom)
        else:
            super().wheelEvent(event)

    def setZoom(self, new_zoom: float):
        """Set the zoom to the appropriate level"""
        zoom_factor = new_zoom / self.zoom
        self.scale(zoom_factor, zoom_factor)
        self.zoom = new_zoom

    def deleteSelected(self):
        """Delete selected items from the current scene."""
        scene = self.scene()
        for selected_item in scene.selectedItems():
            selected_item.remove()
        scene.history.checkpoint("Delete selected elements", set_modified=True)

    def bring_block_forward(self, block: OCBBlock):
        """Move the selected block in front of other blocks.

        Args:
            block: Block to bring forward.

        """
        if self.currentSelectedBlock is not None and not isdeleted(
            self.currentSelectedBlock
        ):
            self.currentSelectedBlock.setZValue(0)
        block.setZValue(1)
        self.currentSelectedBlock = block

    def drag_scene(self, event: QMouseEvent, action="press"):
        """Drag the scene around."""
        if action == "press":
            releaseEvent = QMouseEvent(
                QEvent.Type.MouseButtonRelease,
                event.localPos(),
                event.screenPos(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.NoButton,
                event.modifiers(),
            )
            super().mouseReleaseEvent(releaseEvent)
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            return QMouseEvent(
                event.type(),
                event.localPos(),
                event.screenPos(),
                Qt.MouseButton.LeftButton,
                event.buttons() | Qt.MouseButton.LeftButton,
                event.modifiers(),
            )
        return QMouseEvent(
            event.type(),
            event.localPos(),
            event.screenPos(),
            Qt.MouseButton.LeftButton,
            event.buttons() & ~Qt.MouseButton.LeftButton,
            event.modifiers(),
        )

    def drag_edge(self, event: QMouseEvent, action="press"):
        """Create an edge by drag and drop."""
        item_at_click = self.itemAt(event.pos())
        scene = self.scene()
        if action == "press":
            if (
                isinstance(item_at_click, OCBSocket)
                and self.mode != self.MODE_EDGE_DRAG
                and item_at_click.socket_type != "input"
            ):
                self.mode = self.MODE_EDGE_DRAG
                self.edge_drag = OCBEdge(
                    source_socket=item_at_click,
                    destination=self.mapToScene(event.pos()),
                )
                scene.addItem(self.edge_drag)
                return
        elif action == "release":
            if self.mode == self.MODE_EDGE_DRAG:
                if (
                    isinstance(item_at_click, OCBSocket)
                    and item_at_click is not self.edge_drag.source_socket
                    and item_at_click.socket_type != "output"
                ):
                    self.edge_drag.destination_socket = item_at_click
                    scene.history.checkpoint(
                        "Created edge by dragging", set_modified=True
                    )
                else:
                    self.edge_drag.remove()
                self.edge_drag = None
                self.mode = self.MODE_NOOP
        elif action == "move":
            if self.mode == self.MODE_EDGE_DRAG:
                self.edge_drag.destination = self.mapToScene(event.pos())
        return event

    def set_mode(self, mode: str):
        """Change the view mode.

        Args:
            mode: Mode key to change to, must in present in MODES.

        """
        self.mode = self.MODES[mode]

    def is_mode(self, mode: str):
        """Return True if the view is in the given mode.

        Args:
            mode: Mode key to compare to, must in present in MODES.

        """
        return self.mode == self.MODES[mode]
