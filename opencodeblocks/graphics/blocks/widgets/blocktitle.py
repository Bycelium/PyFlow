
import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFocusEvent, QMouseEvent
from PyQt5.QtWidgets import QLineEdit, QWidget


class OCBTitle(QLineEdit):
    """ The title of an OCBBlock. Needs to be double clicked to interact """

    def __init__(self, content: str, parent: QWidget = None):
        """ Create a new title for an OCBBlock """
        super().__init__(content, parent)
        self.clickTime = None
        self.setReadOnly(True)
        self.setCursorPosition(0)

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
        self.setCursorPosition(0)
        self.deselect()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """ Toggle readonly mode when double clicking """
        self.setReadOnly(not self.isReadOnly())
        if not self.isReadOnly():
            self.setFocus(Qt.MouseFocusReason)
