# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for OCB in block python editor. """

from typing import TYPE_CHECKING, List
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFocusEvent, QFont, QFontMetrics, QColor
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from opencodeblocks.graphics.theme_manager import theme_manager

from opencodeblocks.graphics.blocks.block import OCBBlock


if TYPE_CHECKING:
    from opencodeblocks.graphics.view import OCBView

class PythonEditor(QsciScintilla):

    """ In-block python editor for OpenCodeBlocks. """
    
    def __init__(self, block: OCBBlock):
        """ In-block python editor for OpenCodeBlocks.

        Args:
            block: Block in which to add the python editor widget.

        """
        super().__init__(None)
        self.block = block
        self.setText(self.block.source)

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
        """ Change the font and colors of the editor to match the current theme """
        font = QFont()
        font.setFamily(theme_manager().recommended_font_family)
        font.setFixedPitch(True)
        font.setPointSize(11)
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

    def views(self) -> List['OCBView']:
        """ Get the views in which the python_editor is present. """
        return self.graphicsProxyWidget().scene().views()

    def set_views_mode(self, mode:str):
        """ Set the views in which the python_editor is present to editing mode. """
        for view in self.views():
            if mode == "MODE_EDITING" or view.is_mode("MODE_EDITING"):
                view.set_mode(mode)

    def focusInEvent(self, event: QFocusEvent):
        """ PythonEditor reaction to PyQt focusIn events. """
        self.set_views_mode("MODE_EDITING")
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        """ PythonEditor reaction to PyQt focusOut events. """
        self.set_views_mode("MODE_NOOP")
        if self.isModified():
            self.block.source = self.text()
            self.setModified(False)
        return super().focusInEvent(event)
