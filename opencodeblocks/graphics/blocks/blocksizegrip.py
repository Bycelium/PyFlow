
"""
Implements the SizeGrip Widget for the Blocks.

The size grip is the little icon at the bottom right of a block that is used to
resize a block.
"""

from PyQt5.QtWidgets import QGraphicsItem, QSizeGrip, QWidget
from PyQt5.QtGui import QMouseEvent


class BlockSizeGrip(QSizeGrip):
    def __init__(self, container: QGraphicsItem, parent: QWidget = None):
        """
            Constructor for BlockSizeGrip

            container is the QGraphicsItem holding the QSizeGrip.
            We should have: parent.graphicsProxyWidget().parent() == container
        """
        super().__init__(parent)
        self.mouseX = 0
        self.mouseY = 0
        self.container = container
        self.resizing = False

    def mousePressEvent(self, mouseEvent: QMouseEvent):
        """ Start the resizing """
        self.mouseX = mouseEvent.globalX()
        self.mouseY = mouseEvent.globalY()
        self.resizing = True

    def mouseReleaseEvent(self, mouseEvent: QMouseEvent):
        """ Stop the resizing """
        self.resizing = False

    def mouseMoveEvent(self, mouseEvent: QMouseEvent):
        """ Performs resizing of the root widget """

        deltaX = mouseEvent.globalX() - self.mouseX
        deltaY = mouseEvent.globalY() - self.mouseY
        # Here, we use globalx and globaly instead of x() and y().
        # This is because when using x() and y(), the mouse position is taken
        # relative to the grip, so if the grip moves, the deltaX and deltaY changes.
        # This creates a shaking effect when resizing. We use global to not
        # have this effect.
        new_width = max(
            self.container.width + deltaX,
            self.container._min_width
        )
        new_height = max(
            self.container.height + deltaY,
            self.container._min_height
        )

        self.parent().setGeometry(0, 0, new_width, new_height)
        self.container.update_all()

        self.mouseX = mouseEvent.globalX()
        self.mouseY = mouseEvent.globalY()
