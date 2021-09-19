# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB Window """

from PyQt5.QtWidgets import QGraphicsView, QVBoxLayout, QWidget

from opencodeblocks import __appname__ as application_name
from opencodeblocks.graphics.scene import OCBScene

class OCBWindow(QWidget):

    """ Window for the OCB application. """

    def __init__(self, parent=None, width=800, height=600, x_offset=0, y_offset=0) -> None:
        super().__init__(parent=parent)
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.init_ui()

    def init_ui(self) -> None:
        """ Initialize the user interface of the OCB Window. """
        self.setGeometry(self.x_offset, self.y_offset, self.width, self.height)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Graphics Scene
        self.grScene = OCBScene()

        # Graphics View
        self.view = QGraphicsView(self)
        self.view.setScene(self.grScene)
        self.layout.addWidget(self.view)

        self.setWindowTitle(application_name)
        self.show()
