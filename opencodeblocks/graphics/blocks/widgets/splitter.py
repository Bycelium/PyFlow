# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCBSplitter Widget. """

from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QSplitter, QSplitterHandle, QWidget
from PyQt5.QtGui import QMouseEvent

if TYPE_CHECKING:
    from opencodeblocks.graphics.blocks import OCBBlock


class OCBSplitterHandle(QSplitterHandle):
    """ A handle for splitters with undoable events """

    def mouseReleaseEvent(self, event: 'QMouseEvent'):
        """ When releasing the handle, save the state to history """
        scene = self.parent().block.scene()
        if scene is not None:
            scene.history.checkpoint("Resize block", set_modified=True)
        return super().mouseReleaseEvent(event)


class OCBSplitter(QSplitter):
    """ A spliter with undoable events """

    def __init__(self, block: 'OCBBlock', orientation: int, parent: QWidget):
        """ Create a new OCBSplitter """
        super().__init__(orientation, parent)
        self.block = block

    def createHandle(self):
        """ Return the middle handle of the splitter """
        return OCBSplitterHandle(self.orientation(), self)
