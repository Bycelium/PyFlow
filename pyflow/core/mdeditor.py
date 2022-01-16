# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the PyFlow markdown editor."""

from PyQt5.QtCore import Qt
from PyQt5.Qsci import QsciScintilla

from pyflow.blocks.block import Block
from pyflow.core.editor import Editor


class MarkdownEditor(Editor):

    """In-block markdown editor for Pyflow."""

    def __init__(self, block: Block):
        """In-block markdown editor for Pyflow.

        Args:
            block: Block in which to add the markdown editor widget.

        """
        super().__init__(block)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAutoFillBackground(False)
