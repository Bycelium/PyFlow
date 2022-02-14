# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the MarkdownBlock.

A block able to render Markdown.

"""

from typing import OrderedDict
from markdown import markdown

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.Qsci import QsciLexerMarkdown, QsciScintilla
from PyQt5.QtGui import QColor, QFont
from pyflow.blocks.block import Block
from pyflow.blocks.mdeditor import MarkdownEditor
from pyflow.graphics.theme_manager import theme_manager


class MarkdownBlock(Block):
    """A block that is able to render markdown text."""

    def __init__(self, **kwargs):
        """
        Create a new MarkdownBlock, a block that renders markdown
        """
        super().__init__(block_type="MarkdownBlock", **kwargs)

        self.editor = MarkdownEditor(self)

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
        self.output_panel_background_color = "#1E1E1E"
        self.rendered_markdown.page().setBackgroundColor(
            QColor(self.output_panel_background_color)
        )

        self.splitter.addWidget(self.rendered_markdown)
        self.holder.setWidget(self.root)

        self.setAcceptHoverEvents(True)

    def move_splitter_up(self):
        """Move the splitter to the top of the block.

        This is the viewing mode."""
        self.splitter.setSizes([0, 0])

    def move_splitter_down(self):
        """Move the splitter to the bottom of the block.

        This is the editing mode."""
        self.splitter.setSizes([1, 0])

    def hoverLeaveEvent(self, event: "QGraphicsSceneHoverEvent") -> None:
        """Handle the event when the mouse enters the block."""
        if not self.viewing_is_available():
            self.move_splitter_up()
        return super().hoverLeaveEvent(event)

    def hoverEnterEvent(self, event: "QGraphicsSceneHoverEvent") -> None:
        """Handle the event when the mouse leaves the block."""
        if self.isSelected() and not self.editing_is_available():
            self.move_splitter_down()
        return super().hoverLeaveEvent(event)

    def setSelected(self, selected: bool) -> None:
        """Handle the changes in selection state."""

        # If the user selects the block,
        # and the editing mode is not available,
        # move the splitter down
        if selected and not self.editing_is_available():
            self.move_splitter_down()

        return super().setSelected(selected)

    def editing_is_available(self):
        """Return True if the splitter isn't fully to the top."""
        return self.splitter.sizes()[0] > 0

    def viewing_is_available(self):
        """Return True if the splitter isn't fully to the bottom."""
        return self.splitter.sizes()[1] > 0

    def valueChanged(self):
        """Update markdown rendering when the content of the markdown editor changes."""
        t = self.editor.text()

        dark_theme = f'''
            <style>
                *{{
                    background-color:"""{self.output_panel_background_color}""";
                    color:white;
                }}
            </style>
        '''

        self.rendered_markdown.setHtml(f"{dark_theme}{markdown(t)}")

    @property
    def text(self) -> str:
        """The content of the markdown block."""
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
        """Restore a markdown block from it's serialized state."""
        for dataname in ["text"]:
            if dataname in data:
                setattr(self, dataname, data[dataname])

        super().deserialize(data, hashmap, restore_id)
