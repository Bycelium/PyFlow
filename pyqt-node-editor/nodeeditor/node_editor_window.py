# -*- coding: utf-8 -*-
"""
A module containing the Main Window class
"""
import os, json
from qtpy.QtCore import QSize, QSettings, QPoint
from qtpy.QtWidgets import QMainWindow, QLabel, QAction, QMessageBox, QFileDialog, QApplication
from nodeeditor.node_editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    NodeEditorWidget_class = NodeEditorWidget

    """Class representing NodeEditor's Main Window"""
    def __init__(self):
        """
        :Instance Attributes:

        - **name_company** - name of the company, used for permanent profile settings
        - **name_product** - name of this App, used for permanent profile settings
        """
        super().__init__()

        self.name_company = 'Blenderfreak'
        self.name_product = 'NodeEditor'

        self.initUI()


    def initUI(self):
        """Set up this ``QMainWindow``. Create :class:`~nodeeditor.node_editor_widget.NodeEditorWidget`, Actions and Menus"""
        self.createActions()
        self.createMenus()

        # create node editor widget
        self.nodeeditor = self.__class__.NodeEditorWidget_class(self)
        self.nodeeditor.scene.addHasBeenModifiedListener(self.setTitle)
        self.setCentralWidget(self.nodeeditor)

        self.createStatusBar()

        # set window properties
        # self.setGeometry(200, 200, 800, 600)
        self.setTitle()
        self.show()

    def sizeHint(self):
        return QSize(800, 600)

    def createStatusBar(self):
        """Create Status bar and connect to `Graphics View` scenePosChanged event"""
        self.statusBar().showMessage("")
        self.status_mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        self.nodeeditor.view.scenePosChanged.connect(self.onScenePosChanged)

    def createActions(self):
        """Create basic `File` and `Edit` actions"""
        self.actNew = QAction('&New', self, shortcut='Ctrl+N', statusTip="Create new graph", triggered=self.onFileNew)
        self.actOpen = QAction('&Open', self, shortcut='Ctrl+O', statusTip="Open file", triggered=self.onFileOpen)
        self.actSave = QAction('&Save', self, shortcut='Ctrl+S', statusTip="Save file", triggered=self.onFileSave)
        self.actSaveAs = QAction('Save &As...', self, shortcut='Ctrl+Shift+S', statusTip="Save file as...", triggered=self.onFileSaveAs)
        self.actExit = QAction('E&xit', self, shortcut='Ctrl+Q', statusTip="Exit application", triggered=self.close)

        self.actUndo = QAction('&Undo', self, shortcut='Ctrl+Z', statusTip="Undo last operation", triggered=self.onEditUndo)
        self.actRedo = QAction('&Redo', self, shortcut='Ctrl+Shift+Z', statusTip="Redo last operation", triggered=self.onEditRedo)
        self.actCut = QAction('Cu&t', self, shortcut='Ctrl+X', statusTip="Cut to clipboard", triggered=self.onEditCut)
        self.actCopy = QAction('&Copy', self, shortcut='Ctrl+C', statusTip="Copy to clipboard", triggered=self.onEditCopy)
        self.actPaste = QAction('&Paste', self, shortcut='Ctrl+V', statusTip="Paste from clipboard", triggered=self.onEditPaste)
        self.actDelete = QAction('&Delete', self, shortcut='Del', statusTip="Delete selected items", triggered=self.onEditDelete)


    def createMenus(self):
        """Create Menus for `File` and `Edit`"""
        self.createFileMenu()
        self.createEditMenu()

    def createFileMenu(self):
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)

    def createEditMenu(self):
        menubar = self.menuBar()
        self.editMenu = menubar.addMenu('&Edit')
        self.editMenu.addAction(self.actUndo)
        self.editMenu.addAction(self.actRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCut)
        self.editMenu.addAction(self.actCopy)
        self.editMenu.addAction(self.actPaste)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actDelete)

    def setTitle(self):
        """Function responsible for setting window title"""
        title = "Node Editor - "
        title += self.getCurrentNodeEditorWidget().getUserFriendlyFilename()

        self.setWindowTitle(title)


    def closeEvent(self, event):
        """Handle close event. Ask before we loose work"""
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def isModified(self) -> bool:
        """Has current :class:`~nodeeditor.node_scene.Scene` been modified?

        :return: ``True`` if current :class:`~nodeeditor.node_scene.Scene` has been modified
        :rtype: ``bool``
        """
        nodeeditor = self.getCurrentNodeEditorWidget()
        return nodeeditor.scene.isModified() if nodeeditor else False

    def getCurrentNodeEditorWidget(self) -> NodeEditorWidget:
        """get current :class:`~nodeeditor.node_editor_widget`

        :return: get current :class:`~nodeeditor.node_editor_widget`
        :rtype: :class:`~nodeeditor.node_editor_widget`
        """
        return self.centralWidget()

    def maybeSave(self) -> bool:
        """If current `Scene` is modified, ask a dialog to save the changes. Used before
        closing window / mdi child document

        :return: ``True`` if we can continue in the `Close Event` and shutdown. ``False`` if we should cancel
        :rtype: ``bool``
        """
        if not self.isModified():
            return True

        res = QMessageBox.warning(self, "About to loose your work?",
                "The document has been modified.\n Do you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
              )

        if res == QMessageBox.Save:
            return self.onFileSave()
        elif res == QMessageBox.Cancel:
            return False

        return True


    def onScenePosChanged(self, x:int, y:int):
        """Handle event when cursor position changed on the `Scene`

        :param x: new cursor x position
        :type x:
        :param y: new cursor y position
        :type y:
        """
        self.status_mouse_pos.setText("Scene Pos: [%d, %d]" % (x, y))

    def getFileDialogDirectory(self):
        """Returns starting directory for ``QFileDialog`` file open/save"""
        return ''

    def getFileDialogFilter(self):
        """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
        return 'Graph (*.json);;All files (*)'

    def onFileNew(self):
        """Hande File New operation"""
        if self.maybeSave():
            self.getCurrentNodeEditorWidget().fileNew()
            self.setTitle()


    def onFileOpen(self):
        """Handle File Open operation"""
        if self.maybeSave():
            fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file', self.getFileDialogDirectory(), self.getFileDialogFilter())
            if fname != '' and os.path.isfile(fname):
                self.getCurrentNodeEditorWidget().fileLoad(fname)
                self.setTitle()

    def onFileSave(self):
        """Handle File Save operation"""
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            if not current_nodeeditor.isFilenameSet(): return self.onFileSaveAs()

            current_nodeeditor.fileSave()
            self.statusBar().showMessage("Successfully saved %s" % current_nodeeditor.filename, 5000)

            # support for MDI app
            if hasattr(current_nodeeditor, "setTitle"): current_nodeeditor.setTitle()
            else: self.setTitle()
            return True

    def onFileSaveAs(self):
        """Handle File Save As operation"""
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file', self.getFileDialogDirectory(), self.getFileDialogFilter())
            if fname == '': return False

            self.onBeforeSaveAs(current_nodeeditor, fname)
            current_nodeeditor.fileSave(fname)
            self.statusBar().showMessage("Successfully saved as %s" % current_nodeeditor.filename, 5000)

            # support for MDI app
            if hasattr(current_nodeeditor, "setTitle"): current_nodeeditor.setTitle()
            else: self.setTitle()
            return True

    def onBeforeSaveAs(self, current_nodeeditor: 'NodeEditorWidget', filename: str):
        """
        Event triggered after choosing filename and before actual fileSave(). We are passing current_nodeeditor because
        we will loose focus after asking with QFileDialog and therefore getCurrentNodeEditorWidget will return None
        """
        pass

    def onEditUndo(self):
        """Handle Edit Undo operation"""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.undo()

    def onEditRedo(self):
        """Handle Edit Redo operation"""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.redo()

    def onEditDelete(self):
        """Handle Delete Selected operation"""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.getView().deleteSelected()

    def onEditCut(self):
        """Handle Edit Cut to clipboard operation"""
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self):
        """Handle Edit Copy to clipboard operation"""
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        """Handle Edit Paste from clipboard operation"""
        if self.getCurrentNodeEditorWidget():
            raw_data = QApplication.instance().clipboard().text()

            try:
                data = json.loads(raw_data)
            except ValueError as e:
                print("Pasting of not valid json data!", e)
                return

            # check if the json data are correct
            if 'nodes' not in data:
                print("JSON does not contain any nodes!")
                return

            return self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)

    def readSettings(self):
        """Read the permanent profile settings for this app"""
        settings = QSettings(self.name_company, self.name_product)
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        """Write the permanent profile settings for this app"""
        settings = QSettings(self.name_company, self.name_product)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())