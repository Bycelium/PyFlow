# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for OCB in block python editor. """

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFocusEvent, QFont, QFontMetrics, QColor
from PyQt5.Qsci import QsciScintilla, QsciLexerPython

from opencodeblocks.core.node import Node


class SimplePythonEditor(QsciScintilla):
    ARROW_MARKER_NUM = 8

    def __init__(self, node:Node, parent=None):
        super().__init__(parent)
        self.node = node

        # Set the default font
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(1)
        self.setFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        margins_foreground_color = QColor("#00dddddd")
        margins_background_color = QColor("#E3212121")
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00"))
        self.setMarginLineNumbers(0, True)
        self.setMarginsForegroundColor(margins_foreground_color)
        self.setMarginsBackgroundColor(margins_background_color)

        # Set Python lexer
        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)
        lexer.setDefaultPaper(QColor("#1E1E1E"))
        lexer.setDefaultColor(QColor("#D4D4D4"))

        string_types = [
            QsciLexerPython.SingleQuotedString,
            QsciLexerPython.DoubleQuotedString,
            QsciLexerPython.UnclosedString,
            QsciLexerPython.SingleQuotedFString,
            QsciLexerPython.TripleSingleQuotedString,
            QsciLexerPython.TripleDoubleQuotedString,
            QsciLexerPython.TripleSingleQuotedFString,
            QsciLexerPython.TripleDoubleQuotedFString,
        ]

        for string_type in string_types:
            lexer.setColor(QColor('#CE9178'), string_type)

        lexer.setColor(QColor('#DCDCAA'), QsciLexerPython.FunctionMethodName)
        lexer.setColor(QColor('#569CD6'), QsciLexerPython.Keyword)
        lexer.setColor(QColor('#4EC9B0'), QsciLexerPython.ClassName)
        lexer.setColor(QColor('#7FB347'), QsciLexerPython.Number)
        lexer.setColor(QColor('#D8D8D8'), QsciLexerPython.Operator)

        self.setLexer(lexer)

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

        # Add folding
        self.setFolding(QsciScintilla.FoldStyle.CircledTreeFoldStyle)
        self.setFoldMarginColors(margins_foreground_color, margins_background_color)

        # Add background transparency
        self.setStyleSheet("background:transparent")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

    def set_views_mode(self, mode:str):
        for view in self.graphicsProxyWidget().scene().views():
            if mode == "MODE_EDITING" or view.is_mode("MODE_EDITING"):
                view.set_mode(mode)

    def focusInEvent(self, event: QFocusEvent):
        self.set_views_mode("MODE_EDITING")
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        self.set_views_mode("MODE_NOOP")
        if self.isModified():
            self.node.source = self.text()
            self.setModified(False)
        return super().focusInEvent(event)
