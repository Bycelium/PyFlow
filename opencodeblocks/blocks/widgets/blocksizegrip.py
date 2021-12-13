"""
Implements the SizeGrip Widget for the Blocks.

The size grip is the little icon at the bottom right of a block that is used to
resize a block.
"""

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QGraphicsItem, QSizeGrip, QWidget
from PyQt5.QtGui import QMouseEvent


class OCBSizeGrip(QSizeGrip):
    """A grip to resize a block"""

    def __init__(self, block: QGraphicsItem, parent: QWidget = None):
        """
        Constructor for BlockSizeGrip

        block is the QGraphicsItem holding the QSizeGrip.
        It's usually an OCBBlock
        """
        super().__init__(parent)
        self.mouseX = 0
        self.mouseY = 0
        self.block = block
        self.resizing = False

    def mousePressEvent(self, mouseEvent: QMouseEvent):
        """Start the resizing"""
        self.mouseX = mouseEvent.globalX()
        self.mouseY = mouseEvent.globalY()
        self.resizing = True

    def mouseReleaseEvent(
        self, mouseEvent: QMouseEvent
    ):  # pylint:disable=unused-argument
        """Stop the resizing"""
        self.resizing = False
        self.block.scene().history.checkpoint("Resized block", set_modified=True)

    @property
    def _zoom(self) -> float:
        """Returns how much the scene is"""
        return self.block.scene().views()[0].zoom

    def mouseMoveEvent(self, mouseEvent: QMouseEvent):
        """Performs resizing of the root widget"""
        transformed_pt1 = self.block.mapFromScene(QPoint(0, 0))
        transformed_pt2 = self.block.mapFromScene(QPoint(1, 1))

        pt = transformed_pt2 - transformed_pt1
        pt /= self._zoom

        delta_x = (mouseEvent.globalX() - self.mouseX) * pt.x()
        delta_y = (mouseEvent.globalY() - self.mouseY) * pt.y()
        # Here, we use globalx and globaly instead of x() and y().
        # This is because when using x() and y(), the mouse position is taken
        # relative to the grip, so if the grip moves, the deltaX and deltaY changes.
        # This creates a shaking effect when resizing. We use global to not
        # have this effect.
        new_width = max(self.block.width + int(delta_x), self.block.min_width)
        new_height = max(self.block.height + int(delta_y), self.block.min_height)

        self.parent().setGeometry(0, 0, new_width, new_height)
        self.block.update_all()

        self.mouseX = mouseEvent.globalX()
        self.mouseY = mouseEvent.globalY()
