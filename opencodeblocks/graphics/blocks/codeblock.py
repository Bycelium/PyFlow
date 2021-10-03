# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the base OCB Code Block. """

from typing import Optional, OrderedDict

from PyQt5.QtWidgets import QGraphicsProxyWidget, QGraphicsSceneMouseEvent

from opencodeblocks.core.node import CodeNode
from opencodeblocks.graphics.blocks.block import OCBBlock
from opencodeblocks.graphics.pyeditor import PythonEditor

class OCBCodeBlock(OCBBlock):

    def __init__(self, node: CodeNode, title_color: str = 'white', title_font: str = "Ubuntu",
            title_size: int = 10, title_padding=4, parent: Optional['QGraphicsItem'] = None):
        super().__init__(node, title_color=title_color, title_font=title_font,
            title_size=title_size, title_padding=title_padding, parent=parent)
        self.source_editor = self.init_source_editor()

    def init_source_editor(self):
        source_editor_graphics = QGraphicsProxyWidget(self)
        source_editor = PythonEditor(self.node)
        source_editor.setGeometry(self.edge_size, self.edge_size + self.title_height,
                                  self.width - 2*self.edge_size,
                                  self.height - self.title_height - 2*self.edge_size)
        source_editor_graphics.setWidget(source_editor)
        source_editor_graphics.setZValue(-1)
        return source_editor_graphics

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if self.resizing:
            self.source_editor.widget().setGeometry(self.edge_size,
                self.edge_size + self.title_height, self.width - 2*self.edge_size,
                self.height - self.title_height - 2*self.edge_size)
        return super().mouseMoveEvent(event)
