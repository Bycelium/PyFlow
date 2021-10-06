# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB Widget """

from PyQt5.QtWidgets import QVBoxLayout, QWidget

from opencodeblocks.graphics.scene import OCBScene
from opencodeblocks.graphics.view import OCBView

class OCBWidget(QWidget):

    """ Window for the OCB application. """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Graphics Scene
        self.scene = OCBScene()

        # Graphics View
        self.view = OCBView(self.scene)
        self.layout.addWidget(self.view)
