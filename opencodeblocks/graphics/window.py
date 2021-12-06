# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint:disable=too-many-instance-attributes

""" Module for the OCB Window """

import os
from PyQt5.QtCore import QPoint, QSettings, QSize, Qt, QSignalMapper
from PyQt5.QtGui import QCloseEvent, QKeySequence

from PyQt5.QtWidgets import (
    QDockWidget,
    QListWidget,
    QWidget,
    QAction,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QMdiArea,
)

from opencodeblocks.graphics.widget import OCBWidget
from opencodeblocks.graphics.theme_manager import theme_manager

from opencodeblocks.qss import loadStylesheets


class OCBWindow(QMainWindow):

    """Main window of the OpenCodeBlocks Qt-based application."""

    def __init__(self):
        super().__init__()

        self.stylesheet_filename = os.path.join(
            os.path.dirname(__file__), "..", "qss", "ocb.qss"
        )
        loadStylesheets(
            (
                os.path.join(os.path.dirname(__file__), "..", "qss", "ocb_dark.qss"),
                self.stylesheet_filename,
            )
        )

        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.ViewMode.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsMovable(True)
        self.mdiArea.setTabsClosable(True)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.themeMapper = QSignalMapper(self)
        self.themeMapper.mapped[int].connect(self.setTheme)

        # Menus
        self.createActions()
        self.createMenus()
        self.createToolBars()

        # BlocksDock
        self.createBlocksDock()

        # StatusBar
        self.statusbar = self.statusBar()

        self.updateMenus()

        # Window properties
        self.readSettings()
        self.show()

    def createToolBars(self):
        pass

    def createBlocksDock(self):
        self.block_list = QListWidget()
        self.block_list.addItem("Data loading")
        self.block_list.addItem("Data normalization")
        self.block_list.addItem("Data visualisation")
        self.block_list.addItem("Data preprocessing")
        self.block_list.addItem("Data reshape")
        self.block_list.addItem("Model definition")
        self.block_list.addItem("Model training")
        self.block_list.addItem("Model prediction")
        self.block_list.addItem("Model evaluation")

        self.items = QDockWidget("Blocks")
        self.items.setWidget(self.block_list)
        self.items.setFloating(False)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.items)

    def updateMenus(self):
        pass

    def createActions(self):
        """Create all menu actions."""
        # File
        self._actNew = QAction(
            "&New",
            statusTip="Create new ipygraph",
            shortcut="Ctrl+N",
            triggered=self.onFileNew,
        )
        self._actOpen = QAction(
            "&Open",
            statusTip="Open an ipygraph",
            shortcut="Ctrl+O",
            triggered=self.onFileOpen,
        )
        self._actSave = QAction(
            "&Save",
            statusTip="Save the ipygraph",
            shortcut="Ctrl+S",
            triggered=self.onFileSave,
        )
        self._actSaveAs = QAction(
            "Save &As...",
            statusTip="Save the ipygraph as...",
            shortcut="Ctrl+Shift+S",
            triggered=self.onFileSaveAs,
        )
        self._actSaveAsJupyter = QAction(
            "Save &As ... .ipynb",
            statusTip="Save the ipygraph as a Jupter Notebook at ...",
            triggered=self.oneFileSaveAsJupyter,
        )
        self._actQuit = QAction(
            "&Quit",
            statusTip="Save and Quit the application",
            shortcut="Ctrl+Q",
            triggered=self.close,
        )

        # Edit
        self._actUndo = QAction(
            "&Undo",
            statusTip="Undo last operation",
            shortcut="Ctrl+Z",
            triggered=self.onEditUndo,
        )
        self._actRedo = QAction(
            "&Redo",
            statusTip="Redo last operation",
            shortcut="Ctrl+Y",
            triggered=self.onEditRedo,
        )
        self._actCut = QAction(
            "Cu&t",
            statusTip="Cut to clipboard",
            shortcut="Ctrl+X",
            triggered=self.onEditCut,
        )
        self._actCopy = QAction(
            "&Copy",
            statusTip="Copy to clipboard",
            shortcut="Ctrl+C",
            triggered=self.onEditCopy,
        )
        self._actPaste = QAction(
            "&Paste",
            statusTip="Paste from clipboard",
            shortcut="Ctrl+V",
            triggered=self.onEditPaste,
        )
        self._actDel = QAction(
            "&Del",
            statusTip="Delete selected items",
            shortcut="Del",
            triggered=self.onEditDelete,
        )

        # View
        self._actGlobal = QAction(
            "Global View",
            statusTip="View the hole graph",
            shortcut=" ",
            triggered=self.onViewGlobal,
        )

        # Window
        self._actClose = QAction(
            "Cl&ose",
            self,
            statusTip="Close the active window",
            triggered=self.mdiArea.closeActiveSubWindow,
        )
        self._actCloseAll = QAction(
            "Close &All",
            self,
            statusTip="Close all the windows",
            triggered=self.mdiArea.closeAllSubWindows,
        )
        self._actTile = QAction(
            "&Tile",
            self,
            statusTip="Tile the windows",
            triggered=self.mdiArea.tileSubWindows,
        )
        self._actCascade = QAction(
            "&Cascade",
            self,
            statusTip="Cascade the windows",
            triggered=self.mdiArea.cascadeSubWindows,
        )
        self._actNext = QAction(
            "Ne&xt",
            self,
            shortcut=QKeySequence.StandardKey.NextChild,
            statusTip="Move the focus to the next window",
            triggered=self.mdiArea.activateNextSubWindow,
        )
        self._actPrevious = QAction(
            "Pre&vious",
            self,
            shortcut=QKeySequence.StandardKey.PreviousChild,
            statusTip="Move the focus to the previous window",
            triggered=self.mdiArea.activatePreviousSubWindow,
        )
        self._actSeparator = QAction(self)
        self._actSeparator.setSeparator(True)

    def createMenus(self):
        """Create the File menu with linked shortcuts."""
        self.filemenu = self.menuBar().addMenu("&File")
        self.filemenu.addAction(self._actNew)
        self.filemenu.addAction(self._actOpen)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self._actSave)
        self.filemenu.addAction(self._actSaveAs)
        self.filemenu.addAction(self._actSaveAsJupyter)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self._actQuit)

        self.editmenu = self.menuBar().addMenu("&Edit")
        self.editmenu.addAction(self._actUndo)
        self.editmenu.addAction(self._actRedo)
        self.editmenu.addSeparator()
        self.editmenu.addAction(self._actCut)
        self.editmenu.addAction(self._actCopy)
        self.editmenu.addAction(self._actPaste)
        self.editmenu.addSeparator()
        self.editmenu.addAction(self._actDel)

        self.viewmenu = self.menuBar().addMenu("&View")
        self.thememenu = self.viewmenu.addMenu("Theme")
        self.thememenu.aboutToShow.connect(self.updateThemeMenu)
        self.viewmenu.addAction(self._actGlobal)

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

    def updateThemeMenu(self):
        self.thememenu.clear()
        theme_names = theme_manager().list_themes()
        for i, theme in enumerate(theme_names):
            action = self.thememenu.addAction(theme)
            action.setCheckable(True)
            action.setChecked(i == theme_manager().selected_theme_index)
            action.triggered.connect(self.themeMapper.map)
            self.themeMapper.setMapping(action, i)

    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self._actClose)
        self.windowMenu.addAction(self._actCloseAll)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self._actTile)
        self.windowMenu.addAction(self._actCascade)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self._actNext)
        self.windowMenu.addAction(self._actPrevious)
        self.windowMenu.addAction(self._actSeparator)

        windows = self.mdiArea.subWindowList()
        self._actSeparator.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = f"{i + 1} {child.windowTitle()}"
            if i < 9:
                text = "&" + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.activeMdiChild())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def createNewMdiChild(self, filename: str = None):
        """Create a new graph subwindow loading a file if a path is given."""
        ocb_widget = OCBWidget()
        if filename is not None:
            ocb_widget.scene.load(filename)
            ocb_widget.savepath = filename
        return self.mdiArea.addSubWindow(ocb_widget)

    def onFileNew(self):
        """Create a new file."""
        subwnd = self.createNewMdiChild()
        subwnd.show()

    def onFileOpen(self):
        """Open a file."""
        filename, _ = QFileDialog.getOpenFileName(self, "Open ipygraph from file")
        if filename == "":
            return
        if os.path.isfile(filename):
            subwnd = self.createNewMdiChild(filename)
            subwnd.show()
            self.statusbar.showMessage(f"Successfully loaded {filename}", 2000)

    def onFileSave(self) -> bool:
        """Save file.

        Returns:
            True if the file was successfully saved, False otherwise.

        """
        current_window = self.activeMdiChild()
        if current_window is not None:
            if current_window.savepath is None:
                return self.onFileSaveAs()
            current_window.save()
            self.statusbar.showMessage(
                f"Successfully saved ipygraph at {current_window.savepath}", 2000
            )
        return True

    def onFileSaveAs(self) -> bool:
        """Save file in a given directory, caching savepath for quick save.

        Returns:
            True if the file was successfully saved, False otherwise.

        """
        current_window = self.activeMdiChild()
        if current_window is not None:
            filename, _ = QFileDialog.getSaveFileName(self, "Save ipygraph to file")
            if filename == "":
                return False
            current_window.savepath = filename
            self.onFileSave()
            return True
        return False

    def oneFileSaveAsJupyter(self) -> bool:
        """Save file in a given directory as ipynb, caching savepath for quick save.

        Returns:
            True if the file was successfully saved, False otherwise.

        """
        current_window = self.activeMdiChild()
        if current_window is not None:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save ipygraph to ipynb file"
            )
            if filename == "":
                return False
            current_window.savepath = filename
            current_window.saveAsJupyter()
            self.statusbar.showMessage(
                f"Successfully saved ipygraph as jupter notebook at {current_window.savepath}",
                2000,
            )
            return True
        return False

    @staticmethod
    def is_not_editing(current_window: OCBWidget):
        """True if current_window exists and is not in editing mode."""
        return current_window is not None and not current_window.view.is_mode("EDITING")

    def onEditUndo(self):
        """Undo last operation if not in edit mode."""
        current_window = self.activeMdiChild()
        if self.is_not_editing(current_window):
            current_window.scene.history.undo()

    def onEditRedo(self):
        """Redo last operation if not in edit mode."""
        current_window = self.activeMdiChild()
        if self.is_not_editing(current_window):
            current_window.scene.history.redo()

    def onEditCut(self):
        """Cut the selected items if not in edit mode."""
        current_window = self.activeMdiChild()
        if self.is_not_editing(current_window):
            current_window.scene.clipboard.cut()

    def onEditCopy(self):
        """Copy the selected items if not in edit mode."""
        current_window = self.activeMdiChild()
        if self.is_not_editing(current_window):
            current_window.scene.clipboard.copy()

    def onEditPaste(self):
        """Paste the selected items if not in edit mode."""
        current_window = self.activeMdiChild()
        if self.is_not_editing(current_window):
            current_window.scene.clipboard.paste()

    def onEditDelete(self):
        """Delete the selected items if not in edit mode."""
        current_window = self.activeMdiChild()
        if self.is_not_editing(current_window):
            current_window.view.deleteSelected()

    # def closeEvent(self, event:QEvent):
    #     """ Save and quit the application. """
    #     if self.maybeSave():
    #         event.accept()
    #     else:
    #         event.ignore()

    def closeEvent(self, event: QCloseEvent):
        """Save and quit the application."""
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def maybeSave(self) -> bool:
        """Ask for save and returns if the file should be closed.

        Returns:
            True if the file should be closed, False otherwise.

        """
        if not self.isModified():
            return True

        answer = QMessageBox.warning(
            self,
            "About to loose you work?",
            "The file has been modified.\n" "Do you want to save your changes?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )

        if answer == QMessageBox.StandardButton.Save:
            return self.onFileSave()
        if answer == QMessageBox.StandardButton.Discard:
            return True
        return False

    def activeMdiChild(self) -> OCBWidget:
        """Get the active OCBWidget if existing."""
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow is not None:
            return activeSubWindow.widget()
        return None

    def readSettings(self):
        settings = QSettings("AutopIA", "OpenCodeBlocks")
        pos = settings.value("pos", QPoint(200, 200))
        size = settings.value("size", QSize(400, 400))
        self.move(pos)
        self.resize(size)
        if settings.value("isMaximized", False) == "true":
            self.showMaximized()

    def writeSettings(self):
        settings = QSettings("AutopIA", "OpenCodeBlocks")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())
        settings.setValue("isMaximized", self.isMaximized())

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)

    def onViewGlobal(self):
        """Center the view to see the hole graph"""
        current_window = self.activeMdiChild()
        if current_window is not None and isinstance(current_window, OCBWidget):
            current_window.moveToGlobalView()

    def setTheme(self, theme_index):
        theme_manager().selected_theme_index = theme_index
