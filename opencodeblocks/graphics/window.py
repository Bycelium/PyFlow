# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB Window """

from PyQt5.QtWidgets import QVBoxLayout, QWidget

from opencodeblocks import __appname__ as application_name
from opencodeblocks.graphics.scene import OCBScene
from opencodeblocks.graphics.view import OCBView

class OCBWindow(QWidget):

    """ Window for the OCB application. """

    def __init__(self, parent=None, width=800, height=600, x_offset=0, y_offset=0) -> None:
        super().__init__(parent=parent)
        self.setGeometry(x_offset, y_offset, width, height)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Graphics Scene
        self.scene = OCBScene()

        # Graphics View
        self.view = OCBView(self.scene)
        self.layout.addWidget(self.view)

        self.setWindowTitle(application_name)
        self.show()
