# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the PyFlow editor."""

from typing import TYPE_CHECKING, List
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QFocusEvent,
    QMouseEvent,
)
from PyQt5.Qsci import QsciScintilla

from pyflow.blocks.block import Block

if TYPE_CHECKING:
    from pyflow.graphics.view import View


class Editor(QsciScintilla):

    """In-block editor for Pyflow."""

    def __init__(self, block: Block):
        """In-block editor for Pyflow.

        Args:
            block: Block in which to add the editor widget.

        """
        super().__init__(None)
        self._mode = "NOOP"
        self.block = block

    def views(self) -> List["View"]:
        """Get the views in which the editor is present."""
        return self.block.scene().views()

    @property
    def mode(self) -> int:
        """Editor current mode."""
        return self._mode

    @mode.setter
    def mode(self, value: str):
        self._mode = value
        for view in self.views():
            view.set_mode(value)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Editor reaction to PyQt mousePressEvent events."""
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.mode = "EDITING"
        return super().mousePressEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        """Editor reaction to PyQt focusOut events."""
        self.mode = "NOOP"
        return super().focusOutEvent(event)
