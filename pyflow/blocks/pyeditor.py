# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the PyFlow python editor."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QFocusEvent,
    QFont,
    QFontMetrics,
    QColor,
    QWheelEvent,
)
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from pyflow.core.editor import Editor
from pyflow.graphics.theme_manager import theme_manager

from pyflow.blocks.block import Block

POINT_SIZE = 11


class PythonEditor(Editor):

    """In-block python editor for Pyflow."""

    def __init__(self, block: Block):
        """In-block python editor for Pyflow.

        Args:
            block: Block in which to add the python editor widget.

        """
        super().__init__(block)
        self.foreground_color = QColor("#dddddd")
        self.background_color = QColor("#212121")

        self.update_theme()
        theme_manager().themeChanged.connect(self.update_theme)

        self.fontmetrics = QFontMetrics(self.font())

        # Set caret
        self.setCaretForegroundColor(QColor("#D4D4D4"))

        # Indentation
        self.setAutoIndent(True)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setBackspaceUnindents(True)

        # Disable horizontal scrollbar
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # # Add folding
        self.setFolding(QsciScintilla.FoldStyle.CircledTreeFoldStyle, 1)
        self.setFoldMarginColors(self.background_color, self.background_color)
        self.setMarkerForegroundColor(self.foreground_color, 1)
        self.setMarkerBackgroundColor(self.background_color, 1)

        # Add background transparency
        self.setStyleSheet("background:transparent")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

    def update_theme(self):
        """Change the font and colors of the editor to match the current theme."""
        font = QFont()
        font.setFamily(theme_manager().recommended_font_family)
        font.setFixedPitch(True)
        font.setPointSize(POINT_SIZE)
        self.setFont(font)

        # Margin 0 is used for line numbers
        self.fontmetrics = QFontMetrics(self.font())
        self.setMarginsFont(font)
        self.setMarginWidth(0, self.fontmetrics.width("00") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsForegroundColor(self.foreground_color)
        self.setMarginsBackgroundColor(self.background_color)

        lexer = QsciLexerPython()
        theme_manager().current_theme().apply_to_lexer(lexer)
        lexer.setFont(font)
        self.setLexer(lexer)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """How PythonEditor handles wheel events."""
        if self.mode == "EDITING" and event.angleDelta().x() == 0:
            event.accept()
            return super().wheelEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        """PythonEditor reaction to PyQt focusOut events."""
        self.block.source = self.text()
        return super().focusOutEvent(event)
