# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the base PyFlow Widget."""

import os

from PyQt5.QtWidgets import QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from pyflow.scene import Scene
from pyflow.graphics.view import View
from pyflow.logging import log_init_time, get_logger

LOGGER = get_logger(__name__)


class Widget(QWidget):

    """Widget for a graph visualisation."""

    @log_init_time(LOGGER)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Graphics Scene
        self.scene = Scene()
        self.scene.addHasBeenModifiedListener(self.updateTitle)

        # Graphics View
        self.view = View(self.scene)
        self.layout.addWidget(self.view)

        self.savepath = None

    def updateTitle(self):
        """Update the widget title."""
        if self.savepath is None:
            title = "New Graph"
        else:
            title = os.path.basename(self.savepath)
        if self.isModified():
            title += "*"
        self.setWindowTitle(title)
        LOGGER.debug("Updated widget title to %s", title)

    def isModified(self) -> bool:
        """Return True if the scene has been modified, False otherwise."""
        return self.scene.has_been_modified

    @property
    def savepath(self):
        """Current cached file save path. Update window title when set."""
        return self._savepath

    @savepath.setter
    def savepath(self, value: str):
        self._savepath = value
        self.updateTitle()

    def save(self):
        """Save the current graph to the current save path."""
        self.scene.save(self.savepath)

    def saveAsJupyter(self, filepath: str):
        """Save the current graph notebook as a regular python notebook."""
        self.scene.save_to_ipynb(filepath)

    def load(self, filepath: str):
        """Load a graph from a file."""
        self.scene.load(filepath)
        self.savepath = filepath

    def moveToItems(self):
        """
        Ajust zoom and position to make the whole graph visible.
        If items are selected, then make all the selected items visible instead
        """
        self.view.moveToItems()
