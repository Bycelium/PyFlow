# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB Widget """

import os

from PyQt5.QtWidgets import QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from pyflow.scene import OCBScene
from pyflow.graphics.view import OCBView


class OCBWidget(QWidget):

    """Window for the OCB application."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Graphics Scene
        self.scene = OCBScene()
        self.scene.addHasBeenModifiedListener(self.updateTitle)

        # Graphics View
        self.view = OCBView(self.scene)
        self.layout.addWidget(self.view)

        self.savepath = None

    def updateTitle(self):
        """Update the window title."""
        if self.savepath is None:
            title = "New Graph"
        else:
            title = os.path.basename(self.savepath)
        if self.isModified():
            title += "*"
        self.setWindowTitle(title)

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
        """Save the current graph notebook as a regular python notebook"""
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
