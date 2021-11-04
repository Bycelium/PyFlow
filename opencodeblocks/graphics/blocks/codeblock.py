# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the base OCB Code Block. """

from typing import Optional

from PyQt5.QtCore import Qt, QByteArray
from PyQt5.QtGui import QPainter, QPainterPath, QPixmap
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QWidget, QGraphicsProxyWidget, QLabel

from opencodeblocks.graphics.blocks.block import OCBBlock
from opencodeblocks.graphics.pyeditor import PythonEditor

class OCBCodeBlock(OCBBlock):

    """ Code Block. """

    def __init__(self, **kwargs):
        super().__init__(block_type='code', **kwargs)
        self.source_editor = self.init_source_editor()
        self.display = self.init_display()
        self.stdout = ""
        self.image = ""

    def init_source_editor(self):
        """ Initialize the python source code editor. """
        source_editor_graphics = QGraphicsProxyWidget(self)
        source_editor = PythonEditor(self)
        source_editor.setGeometry(
            int(self.edge_size),
            int(self.edge_size + self.title_height),
            int(self.width - 2*self.edge_size),
            int(self.height - self.title_height - 2*self.edge_size)
        )
        source_editor_graphics.setWidget(source_editor)
        source_editor_graphics.setZValue(-1)
        return source_editor_graphics

    def update_all(self):
        """ Update the code block parts. """
        if hasattr(self, 'source_editor'):
            editor_widget = self.source_editor.widget()
            editor_widget.setGeometry(
                int(self.edge_size),
                int(self.edge_size + self.title_height),
                int(self._width - 2*self.edge_size),
                int(self.height - self.title_height - 2*self.edge_size)
            )
            editor_widget = self.display.widget()
            editor_widget.setGeometry(
                int(self.edge_size),
                int(self.edge_size + self.height),
                int(self.width - 2*self.edge_size),
                int(self.height*0.3 - 2*self.edge_size)
            )
        super().update_all()

    @property
    def source(self) -> str:
        """ Source code. """
        return self._source
    @source.setter
    def source(self, value:str):
        self._source = value
        if hasattr(self, 'source_editor'):
            editor_widget = self.source_editor.widget()
            editor_widget.setText(self._source)

    @property
    def stdout(self) -> str:
        """ Code output. """
        return self._stdout
    @stdout.setter
    def stdout(self, value:str):
        self._stdout = value
        if hasattr(self, 'source_editor'):
            # If there is a text output, erase the image output and display the text output
            self.image = ""
            editor_widget = self.display.widget()
            editor_widget.setText(self._stdout)

    @property
    def image(self) -> str:
        """ Code output. """
        return self._image
    @image.setter
    def image(self, value:str):
        self._image = value
        if hasattr(self, 'source_editor') and self.image != "":
            # If there is an image output, erase the text output and display the image output
            editor_widget = self.display.widget()
            editor_widget.setText("")
            qlabel = editor_widget
            ba = QByteArray.fromBase64(str.encode(self.image))
            pixmap = QPixmap()
            pixmap.loadFromData(ba)
            qlabel.setPixmap(pixmap)

    @source.setter
    def source(self, value:str):
        self._source = value
        if hasattr(self, 'source_editor'):
            editor_widget = self.source_editor.widget()
            editor_widget.setText(self._source)

    def paint(self, painter: QPainter,
            option: QStyleOptionGraphicsItem, #pylint:disable=unused-argument
            widget: Optional[QWidget]=None): #pylint:disable=unused-argument
        """ Paint the output panel """
        super().paint(painter, option, widget)
        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(0, self.height, self.width, 0.3*self.height,
            self.edge_size, self.edge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_title.simplified())

    def init_display(self):
        """ Initialize the ouptput display widget: QLabel """
        display_graphics = QGraphicsProxyWidget(self)
        display = QLabel()
        display.setText("")
        display.setGeometry(
            int(self.edge_size),
            int(self.edge_size + self.height),
            int(self.width - 2*self.edge_size),
            int(self.height*0.3 - 2*self.edge_size)
        )
        display_graphics.setWidget(display)
        display_graphics.setZValue(-1)
        return display_graphics
