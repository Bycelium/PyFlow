# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCBTitle Widget. """

import time
from typing import OrderedDict
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QFocusEvent, QFont, QMouseEvent
from PyQt5.QtWidgets import QLineEdit

from opencodeblocks.serializable import Serializable


class OCBTitle(QLineEdit, Serializable):
    """The title of an OCBBlock. Needs to be double clicked to interact"""

    def __init__(
        self,
        text: str,
        color: str = "white",
        font: str = "Ubuntu",
        size: int = 12,
    ):
        """Create a new title for an OCBBlock

        Args:
            text: Block title.
            color: Color of the block title.
            font: Font of the block title.
            size: Size of the block title.

        """
        Serializable.__init__(self)
        QLineEdit.__init__(self, text, None)
        self.init_ui(color, font, size)
        self.clickTime = None
        self.setReadOnly(True)

    def init_ui(
        self,
        color: str = "white",
        font: str = "Ubuntu",
        size: int = 12,
    ):
        """Apply title parameters

        Args:
            color: Color of the title.
            font: Font of the title.
            size: Size of the title.

        """
        self.setFixedHeight(int(3 * size))
        self.setFont(QFont(font, size))
        self.color = color
        self.setStyleSheet(
            f"""
            QLineEdit {{
                color : {self.color};
                background-color: #FF0000;
                border:none;
            }}"""
        )

    def mousePressEvent(self, event: QMouseEvent):
        """
        Detect double clicks and single clicks are react accordingly by
        dispatching the event to the parent or the current widget
        """
        if self.clickTime is None or (
            self.isReadOnly() and time.time() - self.clickTime > 0.3
        ):
            self.parent().mousePressEvent(event)
        elif self.isReadOnly():
            self.mouseDoubleClickEvent(event)
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
        self.clickTime = time.time()

    def focusOutEvent(self, event: QFocusEvent):
        """The title is read-only when focused is lost"""
        self.setReadOnly(True)
        self.deselect()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Toggle readonly mode when double clicking"""
        self.setReadOnly(not self.isReadOnly())
        if not self.isReadOnly():
            self.setFocus(Qt.FocusReason.MouseFocusReason)

    def serialize(self) -> OrderedDict:
        """Serialize the object as an ordered dictionary."""
        OrderedDict(
            [
                ("id", self.id),
                ("color", self.color),
                ("font", self.font().family()),
                ("size", self.font().pointSize()),
            ]
        )

    def deserialize(
        self, data: OrderedDict, hashmap: dict = None, restore_id=True
    ) -> None:
        """Deserialize the object from an ordered dictionary.

        Args:
            data: Dictionnary containing data do deserialize from.
            hashmap: Dictionnary mapping a hash code into knowed objects.
            restore_id: If True, the id will be restored using the given data.
                If False, a new id will be generated.

        """
        if restore_id:
            self.id = data.get("id", id(self))
        self.init_ui(data["color"], data["font"], data["size"])
