# -*- coding: utf-8 -*-
"""
A module containing ``NodeEditorWidget`` class
"""
import os
from qtpy.QtCore import Qt
from qtpy.QtGui import QBrush, QPen, QFont, QColor
from qtpy.QtWidgets import QWidget, QVBoxLayout, QApplication, QMessageBox, QLabel, QGraphicsItem, QTextEdit, QPushButton

from nodeeditor.node_scene import Scene, InvalidFile
from nodeeditor.node_node import Node
from nodeeditor.node_edge import Edge, EDGE_TYPE_BEZIER
from nodeeditor.node_graphics_view import QDMGraphicsView
from nodeeditor.utils import dumpException


class NodeEditorWidget(QWidget):
    Scene_class = Scene
    GraphicsView_class = QDMGraphicsView

    """The ``NodeEditorWidget`` class"""
    def __init__(self, parent:QWidget=None):
        """
        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance Attributes:

        - **filename** - currently graph's filename or ``None``
        """
        super().__init__(parent)

        self.filename = None

        self.initUI()


    def initUI(self):
        """Set up this ``NodeEditorWidget`` with its layout,  :class:`~nodeeditor.node_scene.Scene` and
        :class:`~nodeeditor.node_graphics_view.QDMGraphicsView`"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # crate graphics scene
        self.scene = self.__class__.Scene_class()

        # create graphics view
        self.view = self.__class__.GraphicsView_class(self.scene.grScene, self)
        self.layout.addWidget(self.view)


    def isModified(self) -> bool:
        """Has the `Scene` been modified?

        :return: ``True`` if the `Scene` has been modified
        :rtype: ``bool``
        """
        return self.scene.isModified()

    def isFilenameSet(self) -> bool:
        """Do we have a graph loaded from file or are we creating a new one?

        :return: ``True`` if filename is set. ``False`` if it is a new graph not yet saved to a file
        :rtype: ''bool''
        """
        return self.filename is not None

    def getSelectedItems(self) -> list:
        """Shortcut returning `Scene`'s currently selected items

        :return: list of ``QGraphicsItems``
        :rtype: list[QGraphicsItem]
        """
        return self.scene.getSelectedItems()

    def hasSelectedItems(self) -> bool:
        """Is there something selected in the :class:`nodeeditor.node_scene.Scene`?

        :return: ``True`` if there is something selected in the `Scene`
        :rtype: ``bool``
        """
        return self.getSelectedItems() != []

    def canUndo(self) -> bool:
        """Can Undo be performed right now?

        :return: ``True`` if we can undo
        :rtype: ``bool``
        """
        return self.scene.history.canUndo()

    def canRedo(self) -> bool:
        """Can Redo be performed right now?

        :return: ``True`` if we can redo
        :rtype: ``bool``
        """
        return self.scene.history.canRedo()

    def getUserFriendlyFilename(self) -> str:
        """Get user friendly filename. Used in the window title

        :return: just a base name of the file or `'New Graph'`
        :rtype: ``str``
        """
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"
        return name + ("*" if self.isModified() else "")

    def fileNew(self):
        """Empty the scene (create new file)"""
        self.scene.clear()
        self.filename = None
        self.scene.history.clear()
        self.scene.history.storeInitialHistoryStamp()

    def fileLoad(self, filename:str):
        """Load serialized graph from JSON file

        :param filename: file to load
        :type filename: ``str``
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.scene.loadFromFile(filename)
            self.filename = filename
            self.scene.history.clear()
            self.scene.history.storeInitialHistoryStamp()
            return True
        except FileNotFoundError as e:
            dumpException(e)
            QMessageBox.warning(self, "Error loading %s" % os.path.basename(filename), str(e).replace('[Errno 2]',''))
            return False
        except InvalidFile as e:
            dumpException(e)
            # QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Error loading %s" % os.path.basename(filename), str(e))
            return False
        finally:
            QApplication.restoreOverrideCursor()


    def fileSave(self, filename:str=None):
        """Save serialized graph to JSON file. When called with an empty parameter, we won't store/remember the filename.

        :param filename: file to store the graph
        :type filename: ``str``
        """
        if filename is not None: self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()
        return True


    def addNodes(self):
        """Testing method to create 3 `Nodes` with 3 `Edges` connecting them"""
        node1 = Node(self.scene, "My Awesome Node 1", inputs=[0,0,0], outputs=[1,5])
        node2 = Node(self.scene, "My Awesome Node 2", inputs=[3,3,3], outputs=[1])
        node3 = Node(self.scene, "My Awesome Node 3", inputs=[2,2,2], outputs=[1])
        node1.setPos(-350, -250)
        node2.setPos(-75, 0)
        node3.setPos(200, -200)

        edge1 = Edge(self.scene, node1.outputs[0], node2.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        edge2 = Edge(self.scene, node2.outputs[0], node3.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        edge3 = Edge(self.scene, node1.outputs[0], node3.inputs[2], edge_type=EDGE_TYPE_BEZIER)

        self.scene.history.storeInitialHistoryStamp()

    def addCustomNode(self):
        """Testing method to create a custom Node with custom content"""
        from nodeeditor.node_content_widget import QDMNodeContentWidget
        from nodeeditor.node_serializable import Serializable

        class NNodeContent(QLabel):  # , Serializable):
            def __init__(self, node, parent=None):
                super().__init__("FooBar")
                self.node = node
                self.setParent(parent)

        class NNode(Node):
            NodeContent_class = NNodeContent

        self.scene.setNodeClassSelector(lambda data: NNode)
        node = NNode(self.scene, "A Custom Node 1", inputs=[0, 1, 2])

        print("node content:", node.content)

    def addDebugContent(self):
        """Testing method to put random QGraphicsItems and elements into QGraphicsScene"""
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)

        rect = self.grScene.addRect(-100, -100, 80, 100, outlinePen, greenBrush)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

        text = self.grScene.addText("This is my Awesome text!", QFont("Ubuntu"))
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setDefaultTextColor(QColor.fromRgbF(1.0, 1.0, 1.0))


        widget1 = QPushButton("Hello World")
        proxy1 = self.grScene.addWidget(widget1)
        proxy1.setFlag(QGraphicsItem.ItemIsMovable)
        proxy1.setPos(0, 30)


        widget2 = QTextEdit()
        proxy2 = self.grScene.addWidget(widget2)
        proxy2.setFlag(QGraphicsItem.ItemIsSelectable)
        proxy2.setPos(0, 60)


        line = self.grScene.addLine(-200, -200, 400, -100, outlinePen)
        line.setFlag(QGraphicsItem.ItemIsMovable)
        line.setFlag(QGraphicsItem.ItemIsSelectable)

