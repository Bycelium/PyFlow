# pylint:disable=unused-argument

import time
from typing import OrderedDict
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFocusEvent, QFont, QMouseEvent
from PyQt5.QtWidgets import QLineEdit, QWidget

from opencodeblocks.core.serializable import Serializable


class OCBTitle(QLineEdit, Serializable):
    """The title of an OCBBlock. Needs to be double clicked to interact"""

    def __init__(
        self,
        text: str,
        color: str = "white",
        font: str = "Ubuntu",
        size: int = 12,
        parent: QWidget = None,
    ):
        """Create a new title for an OCBBlock"""
        Serializable.__init__(self)
        QLineEdit.__init__(self, text, parent)
        self.clickTime = None
        self.init_ui(color, font, size)
        self.setReadOnly(True)
        self.setCursorPosition(0)

    def init_ui(self, color: str, font: str, size: int):
        self.color = color
        self.setStyleSheet(
            f"""
            QLineEdit {{
                color : {self.color};
                background-color: transparent;
                border:none;
            }}"""
        )
        self.setFont(QFont(font, size))

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
        self.setCursorPosition(0)
        self.deselect()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Toggle readonly mode when double clicking"""
        self.setReadOnly(not self.isReadOnly())
        if not self.isReadOnly():
            self.setFocus(Qt.MouseFocusReason)

    def serialize(self) -> OrderedDict:
        return OrderedDict(
            [
                ("color", self.color),
                ("font", self.font().family()),
                ("size", self.font().pointSize()),
            ]
        )

    def deserialize(
        self, data: OrderedDict, hashmap: dict = None, restore_id=True
    ) -> None:
        if restore_id:
            self.id = data.get("id", id(self))
        self.init_ui(data["color"], data["font"], data["size"])
