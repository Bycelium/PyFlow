# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for OCB in block python editor. """

from typing import TYPE_CHECKING, List
from PyQt5.QtCore import QThreadPool, Qt
from PyQt5.QtGui import (
    QFocusEvent,
    QFont,
    QFontMetrics,
    QColor,
    QMouseEvent,
    QWheelEvent,
)
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from opencodeblocks.graphics.theme_manager import theme_manager

from opencodeblocks.blocks.block import OCBBlock
from opencodeblocks.graphics.kernel import Kernel

kernel = Kernel()
threadpool = QThreadPool()

if TYPE_CHECKING:
    from opencodeblocks.graphics.view import OCBView

POINT_SIZE = 11


class PythonEditor(QsciScintilla):

    """In-block python editor for OpenCodeBlocks."""

    def __init__(self, block: OCBBlock):
        """In-block python editor for OpenCodeBlocks.

        Args:
            block: Block in which to add the python editor widget.

        """
        super().__init__(None)
        self._mode = "NOOP"
        self.block = block
        self.kernel = kernel
        self.threadpool = threadpool

        self.update_theme()
        theme_manager().themeChanged.connect(self.update_theme)

        # Set caret
        self.setCaretForegroundColor(QColor("#D4D4D4"))

        # Indentation
        self.setAutoIndent(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setBackspaceUnindents(True)

        # Disable horizontal scrollbar
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # # Add folding
        # self.setFolding(QsciScintilla.FoldStyle.CircledTreeFoldStyle, 1)
        # self.setFoldMarginColors(background_color, background_color)
        # self.setMarkerForegroundColor(foreground_color, 0)
        # self.setMarkerBackgroundColor(background_color, 0)

        # Add background transparency
        self.setStyleSheet("background:transparent")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

    def update_theme(self):
        """Change the font and colors of the editor to match the current theme"""
        font = QFont()
        font.setFamily(theme_manager().recommended_font_family)
        font.setFixedPitch(True)
        font.setPointSize(POINT_SIZE)
        self.setFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        foreground_color = QColor("#dddddd")
        background_color = QColor("#212121")
        self.setMarginsFont(font)
        self.setMarginWidth(2, fontmetrics.width("00") + 6)
        self.setMarginLineNumbers(2, True)
        self.setMarginsForegroundColor(foreground_color)
        self.setMarginsBackgroundColor(background_color)

        lexer = QsciLexerPython()
        theme_manager().current_theme().apply_to_lexer(lexer)
        lexer.setFont(font)
        self.setLexer(lexer)

    def views(self) -> List["OCBView"]:
        """Get the views in which the python_editor is present."""
        return self.block.scene().views()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """How PythonEditor handles wheel events"""
        if self.mode == "EDITING" and event.angleDelta().x() == 0:
            event.accept()
            return super().wheelEvent(event)

    @property
    def mode(self) -> int:
        """PythonEditor current mode"""
        return self._mode

    @mode.setter
    def mode(self, value: str):
        self._mode = value
        for view in self.views():
            view.set_mode(value)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """PythonEditor reaction to PyQt mousePressEvent events."""
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.mode = "EDITING"
        return super().mousePressEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        """PythonEditor reaction to PyQt focusOut events."""
        self.mode = "NOOP"
        self.block.source = self.text()
        return super().focusOutEvent(event)
