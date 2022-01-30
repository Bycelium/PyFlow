# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>
# pylint:disable=unused-argument

""" Module for the Title block widget.

The Title is a modified QLineEdit for PyFlow purpose.
"""

import time
from typing import List, OrderedDict, TYPE_CHECKING
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFocusEvent, QFont, QMouseEvent
from PyQt5.QtWidgets import QLineEdit, QWidget, QGraphicsItem

from pyflow.core.serializable import Serializable

if TYPE_CHECKING:
    from pyflow.graphics.view import View


class Title(QLineEdit, Serializable):
    """The title of an Block. Needs to be double clicked to interact."""

    def __init__(
        self,
        text: str,
        parent_block: QGraphicsItem,
        color: str = "white",
        font: str = "Ubuntu",
        size: int = 12,
        parent_widget: QWidget = None,
    ):
        """Create a new title for an Block."""
        Serializable.__init__(self)
        QLineEdit.__init__(self, text, parent_widget)
        self.clickTime = None
        self.init_ui(color, font, size)
        self.setReadOnly(True)
        self.setCursorPosition(0)
        self.parent_block = parent_block

    def init_ui(self, color: str, font: str, size: int):
        """Apply the style given to the title."""
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

    @property
    def readOnly(self) -> int:
        """PythonEditor current mode."""
        return self.isReadOnly()

    @readOnly.setter
    def readOnly(self, value: bool):
        self.setReadOnly(value)

        new_mode = "NOOP" if value else "EDITING"
        scene = self.parent_block.scene()
        if scene:
            views: List["View"] = scene.views()
            for view in views:
                view.set_mode(new_mode)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Detect double clicks and single clicks are react accordingly by
        dispatching the event to the parent or the current widget
        """
        if self.clickTime is None or (
            self.readOnly and time.time() - self.clickTime > 0.3
        ):
            self.parent().mousePressEvent(event)
        elif self.readOnly:
            self.mouseDoubleClickEvent(event)
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
        self.clickTime = time.time()

    def focusOutEvent(self, event: QFocusEvent):
        """The title is read-only when focused is lost."""
        self.readOnly = True
        self.setCursorPosition(0)
        self.deselect()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Toggle readonly mode when double clicking."""
        self.readOnly = not self.readOnly
        if not self.readOnly:
            self.setFocus(Qt.MouseFocusReason)

    def serialize(self) -> OrderedDict:
        """Return a serialized version of this widget."""
        return OrderedDict(
            [
                ("color", self.color),
                ("font", self.font().family()),
                ("size", self.font().pointSize()),
            ]
        )

    def deserialize(self, data: OrderedDict, hashmap: dict = None, restore_id=True):
        """Restore a title from serialized data."""
        if restore_id:
            self.id = data.get("id", id(self))
        self.init_ui(data["color"], data["font"], data["size"])
