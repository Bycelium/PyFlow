# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the base OCB Code Block. """

from PyQt5.QtWidgets import QGraphicsProxyWidget

from opencodeblocks.graphics.blocks.block import OCBBlock
from opencodeblocks.graphics.pyeditor import PythonEditor

class OCBCodeBlock(OCBBlock):

    def __init__(self, **kwargs):
        super().__init__(block_type='code', **kwargs)
        self.source_editor = self.init_source_editor()

    def init_source_editor(self):
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
        if hasattr(self, 'source_editor'):
            editor_widget = self.source_editor.widget()
            editor_widget.setGeometry(
                int(self.edge_size),
                int(self.edge_size + self.title_height),
                int(self._width - 2*self.edge_size),
                int(self.height - self.title_height - 2*self.edge_size)
            )
        super().update_all()

    @property
    def source(self):
        return self._source
    @source.setter
    def source(self, value:str):
        self._source = value
        if hasattr(self, 'source_editor'):
            editor_widget = self.source_editor.widget()
            editor_widget.setText(self._source)
