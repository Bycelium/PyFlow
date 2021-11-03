# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB Window """

import os
from types import FunctionType
from typing import Optional
from PyQt5.QtCore import QEvent

from PyQt5.QtWidgets import QAction, QFileDialog, QMainWindow, QMenu, QMessageBox

from opencodeblocks import __appname__ as application_name
from opencodeblocks.graphics.view import MODE_EDITING
from opencodeblocks.graphics.widget import OCBWidget

class OCBWindow(QMainWindow):

    """ Main window of the OpenCodeBlocks Qt-based application.

    Args:
        width: Initial window witdh.
        height: Initial window height.
        x_offset: Initial window horizonal offset.
        y_offset: Initial window vertical offset.

    """

    def __init__(self, width:int=800, height:int=600, x_offset:int=0, y_offset:int=0) -> None:
        super().__init__()
        # Cached save path
        self._savepath = None

        # Menus
        self.menubar = self.menuBar()
        self.createFilemenu()
        self.createEditmenu()

        # StatusBar
        self.statusbar = self.statusBar()

        # OCB Widget
        self.ocb_widget = OCBWidget(self)
        self.ocb_widget.scene.addHasBeenModifiedListener(self.changeTitle)
        self.setCentralWidget(self.ocb_widget)

        # Window properties
        self.setGeometry(x_offset, y_offset, width, height)
        self.changeTitle()
        self.show()

    @property
    def savepath(self):
        """ Current cached file save path. Update window title when set."""
        return self._savepath
    @savepath.setter
    def savepath(self, value:str):
        self._savepath = value
        self.changeTitle()

    def changeTitle(self):
        """ Update the window title. """
        title = f"{application_name} - "
        if self.savepath is None:
            title += 'New'
        else:
            title += os.path.basename(self.savepath)
        if self.isModified():
            title += "*"
        self.setWindowTitle(title)

    def addMenuAction(self, menu:QMenu, name:str, trigger_func:FunctionType,
            tooltip:Optional[str]=None, shortcut:Optional[str]=None):
        """ Add an action to a given menu.

        Args:
            menu: Menu in which to add action.
            name: Display name of the action.
            trigger_func: Function to trigger when the action is performed.
            tooltip: Tooltip to show when hovering action.
            shortcut: Shortcut to perform action.

        """
        action = QAction(name, self)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tooltip is not None:
            action.setToolTip(tooltip)
        action.triggered.connect(trigger_func)
        menu.addAction(action)

    def createFilemenu(self):
        """ Create the File menu with linked shortcuts. """
        filemenu = self.menubar.addMenu('&File')
        self.addMenuAction(filemenu, '&New', self.onFileNew, 'Create new ipygraph', 'Ctrl+N')
        filemenu.addSeparator()
        self.addMenuAction(filemenu, '&Open', self.onFileOpen, 'Open an ipygraph', 'Ctrl+O')
        self.addMenuAction(filemenu, '&Save', self.onFileSave, 'Save the ipygraph', 'Ctrl+S')
        self.addMenuAction(filemenu, 'Save &As...',
            self.onFileSaveAs, 'Save the graph as...', 'Ctrl+Shift+S')
        filemenu.addSeparator()
        self.addMenuAction(filemenu, '&Quit', self.close, 'Save and Quit the application', 'Ctrl+Q')

    def onFileNew(self):
        """ Create a new file. """
        if self.maybeSave():
            self.ocb_widget.scene.clear()
            self.savepath = None

    def onFileOpen(self):
        """ Open a file. """
        if self.maybeSave():
            filename, _ = QFileDialog.getOpenFileName(self, 'Open ipygraph from file')
            if filename == '':
                return
            if os.path.isfile(filename):
                self.ocb_widget.scene.load(filename)
                self.statusbar.showMessage(f"Successfully loaded {filename}")
                self.savepath = filename

    def onFileSave(self) -> bool:
        """ Save file.

        Returns:
            True if the file was successfully saved, False otherwise.

        """
        if self.savepath is None:
            return self.onFileSaveAs()
        self.ocb_widget.scene.save(self.savepath)
        self.statusbar.showMessage(f"Successfully saved ipygraph {self.savepath}")
        return True

    def onFileSaveAs(self) -> bool:
        """ Save file in a given directory, caching savepath for quick save.

        Returns:
            True if the file was successfully saved, False otherwise.

        """
        filename, _ = QFileDialog.getSaveFileName(self, 'Save ipygraph to file')
        if filename == '':
            return False
        if os.path.isfile(filename):
            self.savepath = filename
        self.onFileSave()
        return True

    def createEditmenu(self):
        """ Create the Edit menu with linked shortcuts. """
        editmenu = self.menubar.addMenu('&Edit')
        self.addMenuAction(editmenu, '&Undo', self.onEditUndo,'Undo last operation', 'Ctrl+Z')
        self.addMenuAction(editmenu, '&Redo', self.onEditRedo, 'Redo last operation', 'Ctrl+Y')
        self.addMenuAction(editmenu, 'Cu&t', self.onEditCut, 'Cut to clipboard', 'Ctrl+X')
        self.addMenuAction(editmenu, '&Copy', self.onEditCopy, 'Copy to clipboard', 'Ctrl+C')
        self.addMenuAction(editmenu, '&Paste', self.onEditPaste, 'Paste from clipboard', 'Ctrl+V')
        self.addMenuAction(editmenu, '&Del', self.onEditDelete, 'Delete selected items', 'Del')

    def onEditUndo(self):
        """ Undo last operation if not in edit mode. """
        if self.ocb_widget.view.mode != MODE_EDITING:
            self.ocb_widget.scene.history.undo()

    def onEditRedo(self):
        """ Redo last operation if not in edit mode. """
        if self.ocb_widget.view.mode != MODE_EDITING:
            self.ocb_widget.scene.history.redo()

    def onEditCut(self):
        """ Cut the selected items if not in edit mode. """
        if self.ocb_widget.view.mode != MODE_EDITING:
            self.ocb_widget.scene.clipboard.cut()

    def onEditCopy(self):
        """ Copy the selected items if not in edit mode. """
        if self.ocb_widget.view.mode != MODE_EDITING:
            self.ocb_widget.scene.clipboard.copy()

    def onEditPaste(self):
        """ Paste the selected items if not in edit mode. """
        if self.ocb_widget.view.mode != MODE_EDITING:
            self.ocb_widget.scene.clipboard.paste()

    def onEditDelete(self):
        """ Delete the selected items if not in edit mode. """
        if self.ocb_widget.view.mode != MODE_EDITING:
            self.ocb_widget.view.deleteSelected()

    def closeEvent(self, event:QEvent):
        """ Save and quit the application. """
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def isModified(self) -> bool:
        """ Return True if the scene has been modified, False otherwise. """
        return self.centralWidget().scene.has_been_modified

    def maybeSave(self) -> bool:
        """ Ask for save and returns if the file should be closed.

        Returns:
            True if the file should be closed, False otherwise.

        """
        if not self.isModified():
            return True

        answer = QMessageBox.warning(self, "About to loose you work?",
            "The file has been modified.\n Do you want to save your changes?",
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )

        if answer == QMessageBox.StandardButton.Save:
            return self.onFileSave()
        if answer == QMessageBox.StandardButton.Discard:
            return True
        return False
