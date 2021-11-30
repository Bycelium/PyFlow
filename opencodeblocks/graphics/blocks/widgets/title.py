# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCBTitle Widget. """

import time
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QFocusEvent, QFont, QMouseEvent
from PyQt5.QtWidgets import QLineEdit


class OCBTitle(QLineEdit):
    """ The title of an OCBBlock. Needs to be double clicked to interact """

    def __init__(self, text: str, color: str = 'white', font: str = "Ubuntu",
                 size: int = 12, padding=4.0, left_offset=4):
        """ Create a new title for an OCBBlock

        Args:
            text: Block title.
            color: Color of the block title.
            font: Font of the block title.
            size: Size of the block title.
            padding: Padding of the block title.

        """
        super().__init__(text, None)
        self.setFixedHeight(int(3.5 * size))
        self.setFont(QFont(font, size))
        self.color = color
        self.padding = padding
        self.left_offset = left_offset
        self.setStyleSheet(
            f"""
            QLineEdit {{
                color : {self.color};
                background-color: #E3212121;
                border:none;
                padding: {self.padding}px;
            }}"""
        )
        self.clickTime = None
        self.setReadOnly(True)

    @property
    def metadatas(self) -> dict:
        return {
            'color': self.color,
            'font': self.font().family(),
            'size': self.font().pointSize(),
            'padding': self.padding,
        }

    def mousePressEvent(self, event: QMouseEvent):
        """
        Detect double clicks and single clicks are react accordingly by
        dispatching the event to the parent or the current widget
        """
        if self.clickTime is None or (
                self.isReadOnly() and time.time() - self.clickTime > 0.3):
            self.parent().mousePressEvent(event)
        elif self.isReadOnly():
            self.mouseDoubleClickEvent(event)
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
        self.clickTime = time.time()

    def focusOutEvent(self, event: QFocusEvent):
        """ The title is read-only when focused is lost """
        self.setReadOnly(True)
        self.deselect()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """ Toggle readonly mode when double clicking """
        self.setReadOnly(not self.isReadOnly())
        if not self.isReadOnly():
            self.setFocus(Qt.FocusReason.MouseFocusReason)
