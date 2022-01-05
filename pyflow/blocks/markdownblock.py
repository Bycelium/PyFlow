"""
Exports OCBMarkdownBlock.
"""

from typing import OrderedDict
from markdown import markdown

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.Qsci import QsciLexerMarkdown, QsciScintilla
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from pyflow.blocks.block import OCBBlock
from pyflow.graphics.theme_manager import theme_manager


class OCBMarkdownBlock(OCBBlock):
    """A block that is able to render markdown text"""

    def __init__(self, **kwargs):
        """
        Create a new OCBMarkdownBlock, a block that renders markdown
        """
        super().__init__(**kwargs)

        self.editor = QsciScintilla()
        self.editor.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        self.editor.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.editor.setAutoFillBackground(False)

        self.lexer = QsciLexerMarkdown()
        theme_manager().current_theme().apply_to_lexer(self.lexer)
        self.lexer.setColor(QColor.fromRgb(255, 255, 255), -1)
        self.editor.setCaretForegroundColor(QColor("#FFFFFF"))
        self.editor.setLexer(self.lexer)

        font = QFont()
        font.setFamily(theme_manager().recommended_font_family)
        font.setFixedPitch(True)
        font.setPointSize(11)
        self.editor.setFont(font)
        self.editor.setMarginWidth(QsciScintilla.SC_MARGIN_NUMBER, 0)
        self.editor.setStyleSheet("background:transparent")
        self.editor.textChanged.connect(self.valueChanged)

        self.splitter.addWidget(self.editor)

        self.rendered_markdown = QWebEngineView()
        self.rendered_markdown.page().setBackgroundColor(
            QColor.fromRgba64(0, 0, 0, alpha=0)
        )

        self.splitter.addWidget(self.rendered_markdown)
        self.holder.setWidget(self.root)

    def valueChanged(self):
        """Update markdown rendering when the content of the markdown editor changes"""
        t = self.editor.text()

        dark_theme = """
            <style>
                *{
                    background-color:transparent;
                    color:white;
                }
            </style>
        """

        self.rendered_markdown.setHtml(f"{dark_theme}{markdown(t)}")

    @property
    def text(self) -> str:
        """The content of the markdown block"""
        return self.editor.text()

    @text.setter
    def text(self, value: str):
        self.editor.setText(value)
        self.valueChanged()

    def serialize(self):
        base_dict = super().serialize()
        base_dict["text"] = self.text

        return base_dict

    def deserialize(
        self, data: OrderedDict, hashmap: dict = None, restore_id: bool = True
    ):
        """Restore a markdown block from it's serialized state"""
        for dataname in ["text"]:
            if dataname in data:
                setattr(self, dataname, data[dataname])

        super().deserialize(data, hashmap, restore_id)
