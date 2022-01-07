"""
Module defining a Splitter, the widget that contains multiple areas inside
a block and allows the user to resize those areas.
"""

from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QSplitter, QSplitterHandle, QWidget


class SplitterHandle(QSplitterHandle):
    """A handle for splitters with undoable events"""

    def mouseReleaseEvent(self, evt: QMouseEvent):
        """When releasing the handle, save the state to history"""
        scene = self.parent().block.scene()
        if scene is not None:
            scene.history.checkpoint("Resize block", set_modified=True)
        return super().mouseReleaseEvent(evt)


class Splitter(QSplitter):
    """A spliter with undoable events"""

    def __init__(self, block: QWidget, orientation: int, parent: QWidget):
        """Create a new Splitter"""
        super().__init__(orientation, parent)
        self.block = block

    def createHandle(self):
        """Return the middle handle of the splitter"""
        return SplitterHandle(self.orientation(), self)
