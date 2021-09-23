# -*- coding: utf-8 -*-
"""A module containing the base class for the Node's content graphical representation. It also contains an example of
an overridden Text Widget, which can pass a notification to it's parent about being modified."""
from collections import OrderedDict
from nodeeditor.node_serializable import Serializable
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextEdit
from PyQt5.Qsci import QsciScintilla, QsciLexerPython

class Editor(QsciScintilla):
    def __init__(self):
        super().__init__()
        font = self.font()
        font.setFamily('mono')
        self.setFont(font)
        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)

class QDMNodeContentWidget(QWidget, Serializable):
    """Base class for representation of the Node's graphics content. This class also provides layout
    for other widgets inside of a :py:class:`~nodeeditor.node_node.Node`"""
    def __init__(self, node:'Node', parent:QWidget=None):
        """
        :param node: reference to the :py:class:`~nodeeditor.node_node.Node`
        :type node: :py:class:`~nodeeditor.node_node.Node`
        :param parent: parent widget
        :type parent: QWidget

        :Instance Attributes:
            - **node** - reference to the :class:`~nodeeditor.node_node.Node`
            - **layout** - ``QLayout`` container
        """
        self.node = node
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        """Sets up layouts and widgets to be rendered in :py:class:`~nodeeditor.node_graphics_node.QDMGraphicsNode` class.
        """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.wdg_label = QLabel("Some Title")
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(Editor())

    def setEditingFlag(self, value:bool):
        """
        .. note::

            If you are handling keyPress events by default Qt Window's shortcuts and ``QActions``, you will not
             need to use this method.

        Helper function which sets editingFlag inside :py:class:`~nodeeditor.node_graphics_view.QDMGraphicsView` class.

        This is a helper function to handle keys inside nodes with ``QLineEdits`` or ``QTextEdits`` (you can
        use overridden :py:class:`QDMTextEdit` class) and with QGraphicsView class method ``keyPressEvent``.

        :param value: new value for editing flag
        """
        self.node.scene.getView().editingFlag = value

    def serialize(self) -> OrderedDict:
        return OrderedDict([
        ])

    def deserialize(self, data:dict, hashmap:dict={}, restore_id:bool=True) -> bool:
        return True

class QDMTextEdit(QTextEdit):
    """
        .. note::

            This class is an example of a ``QTextEdit`` modification that handles the `Delete` key event with an overridden
            Qt's ``keyPressEvent`` (when not using ``QActions`` in menu or toolbar)

        Overridden ``QTextEdit`` which sends a notification about being edited to its parent's container :py:class:`QDMNodeContentWidget`
    """
    def focusInEvent(self, event:'QFocusEvent'):
        """Example of an overridden focusInEvent to mark the start of editing

        :param event: Qt's focus event
        :type event: QFocusEvent
        """
        self.parentWidget().setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event:'QFocusEvent'):
        """Example of an overridden focusOutEvent to mark the end of editing

        :param event: Qt's focus event
        :type event: QFocusEvent
        """
        self.parentWidget().setEditingFlag(False)
        super().focusOutEvent(event)
