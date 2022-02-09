# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for View."""

import json
import os
import pathlib
from typing import List, Optional, Tuple

from PyQt5.QtCore import QEvent, QPoint, QPointF, Qt
from PyQt5.QtGui import QKeyEvent, QMouseEvent, QPainter, QWheelEvent, QContextMenuEvent
from PyQt5.QtWidgets import QGraphicsView, QMenu, QApplication
from PyQt5.sip import isdeleted
from pyflow.blocks.codeblock import CodeBlock
from pyflow.blocks.executableblock import ExecutableBlock
from pyflow.core.add_edge_button import AddEdgeButton

from pyflow.scene import Scene
from pyflow.core.socket import Socket
from pyflow.core.edge import Edge
from pyflow.blocks.block import Block
from pyflow.blocks import __file__ as BLOCK_INIT_PATH

BLOCK_PATH = pathlib.Path(BLOCK_INIT_PATH).parent
BLOCKFILES_PATH = os.path.join(BLOCK_PATH, "blockfiles")

EPS: float = 1e-10  # To check if blocks are of size 0


class View(QGraphicsView):

    """View for the Window."""

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
        scene: Scene,
        parent=None,
        zoom_step: float = 1.25,
        zoom_min: float = 0.05,
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
        """Initialize the custom  View UI."""
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

    def scene(self) -> Scene:
        """Get current Scene."""
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
        """Dispatch Qt's mouseRelease events to corresponding functions below."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """View reaction to mouseMoveEvent."""
        self.lastMousePos = self.mapToScene(event.pos())
        self.drag_edge(event, "move")
        if event is not None:
            super().mouseMoveEvent(event)

    def leftMouseButtonPress(self, event: QMouseEvent):
        """View reaction to leftMouseButtonPress event."""
        # If clicked on a block, bring it forward.
        item_at_click = self.itemAt(event.pos())
        if item_at_click is not None:
            while item_at_click.parentItem() is not None:
                if isinstance(item_at_click, Block):
                    break
                item_at_click = item_at_click.parentItem()

            if isinstance(item_at_click, Block):
                self.bring_block_forward(item_at_click)

        # If Ctrl + left click on a socket, toggle its state
        event = self.toggle_socket(event)

        # If clicked on a socket or the add edge button, start dragging an edge.
        event = self.drag_edge(event, "press")
        if event is not None:
            super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event: QMouseEvent):
        """View reaction to leftMouseButtonRelease event."""
        event = self.drag_edge(event, "release")
        if event is not None:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event: QMouseEvent):
        """View reaction to middleMouseButtonPress event."""
        if self.itemAt(event.pos()) is None:
            event = self.drag_scene(event, "press")
        super().mousePressEvent(event)

    def middleMouseButtonRelease(self, event: QMouseEvent):
        """View reaction to middleMouseButtonRelease event."""
        event = self.drag_scene(event, "release")
        super().mouseReleaseEvent(event)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def centerView(self, x: float, y: float):
        """Move the view so that the position (x,y) is centered."""
        hsb = self.horizontalScrollBar()
        vsb = self.verticalScrollBar()
        hsb.setValue(x * self.zoom - self.width() / 2)
        vsb.setValue(y * self.zoom - self.height() / 2)

    def moveToItems(self) -> bool:
        """Ajust zoom and position to make selected items visible.

        If no item is selected, make the whole graph visible instead.

        Returns:
            True if the event was handled, False otherwise.
        """

        items = self.scene().items()

        # If items are selected, overwride the behvaior
        if len(self.scene().selectedItems()) > 0:
            items = self.scene().selectedItems()

        code_blocks: List[Block] = [i for i in items if isinstance(i, Block)]

        if not code_blocks:
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

        # Operate the zoom
        # If there is only one item, don't make it very big
        if len(code_blocks) == 1:
            self.setZoom(1)
        else:
            self.setZoom(min(required_zoom_x, required_zoom_y))

        # Operate the translation
        self.centerView(center_x, center_y)

        return True

    def getDistanceToCenter(self, x: float, y: float) -> Tuple[float]:
        """Return the vector from the (x,y) position given to the center of the view."""
        ypos = self.verticalScrollBar().value()
        xpos = self.horizontalScrollBar().value()
        return (
            xpos - x * self.zoom + self.width() / 2,
            ypos - y * self.zoom + self.height() / 2,
        )

    def moveViewOnArrow(self, event: QKeyEvent) -> bool:
        """
        View reaction to an arrow key being pressed.
        Returns True if the event was handled.
        """
        # The focusItem has priority for this event if it is a source editor
        # if self.scene().focusItem() is not None:
        if self.mode == View.MODE_EDITING:
            return False
            # parent = self.scene().focusItem().parentItem()
            # if isinstance(parent, CodeBlock) and parent.source_editor.hasFocus():
            #     return False

        n_selected_items = len(self.scene().selectedItems())
        if n_selected_items > 1:
            return False

        code_blocks = [
            i
            for i in self.scene().items()
            if isinstance(i, Block) and not i.isSelected()
        ]

        reference = None
        if n_selected_items == 1 and isinstance(self.scene().selectedItems()[0], Block):
            selected_item = self.scene().selectedItems()[0]
            reference = QPoint(
                selected_item.x() + selected_item.width / 2,
                selected_item.y() + selected_item.height / 2,
            )
            self.scene().clearSelection()
            self.bring_block_forward(selected_item)

        dist_array = []
        for block in code_blocks:
            block_center_x = block.x() + block.width / 2
            block_center_y = block.y() + block.height / 2
            if reference is None:
                xdist, ydist = self.getDistanceToCenter(block_center_x, block_center_y)
            else:
                xdist = reference.x() - block_center_x
                ydist = reference.y() - block_center_y
            dist_array.append((block_center_x, block_center_y, -xdist, -ydist))

        def in_region(x, y, key):
            up_right = x / self.width() - y / self.height() >= 0
            down_right = x / self.width() + y / self.height() >= 0
            if key == Qt.Key.Key_Up:
                return up_right and not down_right
            if key == Qt.Key.Key_Down:
                return not up_right and down_right
            if key == Qt.Key.Key_Left:
                return not up_right and not down_right
            if key == Qt.Key.Key_Right:
                return up_right and down_right

        key_id = event.key()
        dist_array = filter(lambda pos: in_region(pos[2], pos[3], key_id), dist_array)
        dist_array = list(dist_array)
        if not dist_array:
            return False

        def oriented_distance(x, y, key):
            if key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
                return abs(y) / self.height() + (x / self.width()) ** 2
            if key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
                return abs(x) / self.width() + (y / self.height()) ** 2

        dist_array.sort(key=lambda pos: oriented_distance(pos[2], pos[3], key_id))
        block_center_x, block_center_y, _, _ = dist_array[0]

        item_to_navigate = self.scene().itemAt(
            block_center_x, block_center_y, self.transform()
        )
        self.scene().clearSelection()
        if isinstance(item_to_navigate.parentItem(), Block):
            item_to_navigate.parentItem().setSelected(True)

        self.centerView(block_center_x, block_center_y)
        return True

    def keyPressEvent(self, event: QKeyEvent):
        """View reaction to a key being pressed."""
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
        block_type_files = os.listdir(BLOCKFILES_PATH)
        block_types = []
        for blockfile_name in block_type_files:
            filepath = os.path.join(BLOCKFILES_PATH, blockfile_name)
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
        """Displays the context menu when inside a view."""
        super().contextMenuEvent(event)
        # If somebody has already accepted the event, don't handle it.
        if event.isAccepted():
            return
        event.setAccepted(True)

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
            self.setZoom(new_zoom)
        else:
            super().wheelEvent(event)

    def setZoom(self, new_zoom: float):
        """Set the zoom to the appropriate level."""

        # Constrain the zoom level
        if new_zoom > self.zoom_max:
            new_zoom = self.zoom_max
        if new_zoom < self.zoom_min:
            new_zoom = self.zoom_min

        zoom_factor = new_zoom / self.zoom
        self.scale(zoom_factor, zoom_factor)
        self.zoom = new_zoom

    def deleteSelected(self):
        """Delete selected items from the current scene."""
        scene = self.scene()
        for selected_item in scene.selectedItems():
            selected_item.remove()
        scene.history.checkpoint("Delete selected elements", set_modified=True)

    def bring_block_forward(self, block: Block):
        """Move the selected block in front of other blocks.

        Args:
            block: Block to bring forward.

        """
        if self.currentSelectedBlock is not None and not isdeleted(
            self.currentSelectedBlock
        ):
            self.currentSelectedBlock.setZValue(0)
        block.setZValue(1)
        block.setSelected(True)
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

    def get_block_below_mouse(
        self, mouse_position: QPoint
    ) -> Optional[ExecutableBlock]:
        """Get the first ExecutableBlock below the mouse.

        If there is none, return None"""
        # All the items below the mouse
        items_below_click = self.items(mouse_position)

        for item in items_below_click:
            if isinstance(item, CodeBlock):
                return item
            # Also checks blocks sockets because they extend slightly outside the block
            if (
                isinstance(item, Socket)
                and isinstance(item.block, ExecutableBlock)
                and item.socket_type == "input"
            ):
                return item.block

        return None

    def drag_edge(self, event: QMouseEvent, action="press"):
        """Create an edge by drag and drop."""

        # edge creation / destruction if control is pressed
        if event is None or (
            action != "move"
            and QApplication.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            return event

        # The item on top of everything else, below the mouse
        item_at_click = self.itemAt(event.pos())

        scene = self.scene()
        if action == "press":
            # If it is an existing edge, deleted the old edge and create a new one
            if (
                isinstance(item_at_click, Socket)
                and self.mode != self.MODE_EDGE_DRAG
                and item_at_click.socket_type != "input"
            ):
                while item_at_click.edges:
                    edge = item_at_click.edges[0]
                    old_destination = edge.destination_socket
                    old_destination.remove()

                self.mode = self.MODE_EDGE_DRAG
                self.edge_drag = Edge(
                    source_socket=item_at_click,
                    destination=self.mapToScene(event.pos()),
                )
                scene.addItem(self.edge_drag)
                return
            # If it is the add edge button, create a new edge and a new socket for this edge
            elif (
                isinstance(item_at_click, AddEdgeButton)
                and self.mode != self.MODE_EDGE_DRAG
            ):
                self.mode = self.MODE_EDGE_DRAG
                new_socket = item_at_click.block.create_new_output_socket()
                self.edge_drag = Edge(
                    source_socket=new_socket,
                    destination=self.mapToScene(event.pos()),
                )
                scene.addItem(self.edge_drag)
                return
        elif action == "release":
            if self.mode == self.MODE_EDGE_DRAG:

                block_below_mouse = self.get_block_below_mouse(event.pos())

                if (
                    block_below_mouse is not None
                    and block_below_mouse is not self.edge_drag.source_socket.block
                ):
                    input_socket = block_below_mouse.create_new_input_socket()
                    self.edge_drag.destination_socket = input_socket
                    scene.history.checkpoint(
                        "Created edge by dragging", set_modified=True
                    )
                else:
                    self.edge_drag.source_socket.remove()
                self.edge_drag = None
                self.mode = self.MODE_NOOP
                self.scene().update_all_blocks_sockets()
        elif action == "move":
            if self.mode == self.MODE_EDGE_DRAG:
                self.edge_drag.destination = self.mapToScene(event.pos())
                self.scene().update_all_blocks_sockets()
        return event

    def toggle_socket(self, event: QMouseEvent) -> Optional[QMouseEvent]:
        """Toggle the socket.

        Return None if the event has been handeln, otherwise return the input event"""

        if QApplication.keyboardModifiers() != Qt.KeyboardModifier.ControlModifier:
            return event
        item_at_click = self.itemAt(event.pos())
        if not isinstance(item_at_click, Socket):
            return event

        item_at_click.toggle()
        return None

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
