# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB Window """

import os
from types import FunctionType
from typing import Optional

from PyQt5.QtWidgets import QAction, QFileDialog, QMainWindow, QMenu

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

        # Menus
        self.menubar = self.menuBar()
        self.createFilemenu()
        self.createEditmenu()

        # StatusBar
        self.statusbar = self.statusBar()

        # OCB Widget
        self.ocb_widget = OCBWidget(self)
        self.setCentralWidget(self.ocb_widget)

        # Window properties
        self.setGeometry(x_offset, y_offset, width, height)
        self.setWindowTitle(application_name)
        self.show()

        # Cached save path
        self.savepath = None

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
        self.ocb_widget.scene.clear()
        self.savepath = None

    def onFileOpen(self):
        """ Open a file. """
        filename, _ = QFileDialog.getOpenFileName(self, 'Open ipygraph from file')
        if filename == '':
            return
        if os.path.isfile(filename):
            self.ocb_widget.scene.load(filename)
            self.statusbar.showMessage(f"Successfully loaded {filename}")

    def onFileSave(self):
        """ Save file. """
        if self.savepath is None:
            self.onFileSaveAs()
        if self.savepath is None:
            return
        self.ocb_widget.scene.save(self.savepath)
        self.statusbar.showMessage(f"Successfully saved ipygraph {self.savepath}")

    def onFileSaveAs(self):
        """ Save file in a given directory, caching savepath for quick save. """
        filename, _ = QFileDialog.getSaveFileName(self, 'Save ipygraph to file')
        if filename == '':
            return
        if os.path.isfile(filename):
            self.savepath = filename
        self.onFileSave()

    def createEditmenu(self):
        """ Create the Edit menu with linked shortcuts. """
        editmenu = self.menubar.addMenu('&Edit')
        self.addMenuAction(editmenu, '&Undo', self.onEditUndo, 'Undo last operation', 'Ctrl+Z')
        self.addMenuAction(editmenu, '&Redo', self.onEditRedo, 'Redo last operation', 'Ctrl+Y')
        self.addMenuAction(editmenu, '&Del', self.onEditDelete, 'Delete selected items', 'Del')

    def onEditUndo(self):
        """ Undo last operation if not in edit mode. """
        if self.ocb_widget.view.mode != MODE_EDITING:
            self.ocb_widget.scene.history.undo()

    def onEditRedo(self):
        """ Redo last operation if not in edit mode. """
        if self.ocb_widget.view.mode != MODE_EDITING:
            self.ocb_widget.scene.history.undo()

    def onEditDelete(self):
        """ Delete the selected items if not in edit mode. """
        if self.ocb_widget.view.mode != MODE_EDITING:
            self.ocb_widget.view.deleteSelected()

    def close(self) -> bool:
        """ Save and quit the application. """
        self.onFileSave()
        return super().close()
