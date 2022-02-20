# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>
# pylint:disable=too-many-instance-attributes, unsubscriptable-object

""" Module for the base Window."""

import os
import pathlib

from PyQt5.QtCore import QPoint, QSettings, QSize, Qt, QSignalMapper
from PyQt5.QtGui import QCloseEvent, QKeySequence
from PyQt5.QtWidgets import (
    QWidget,
    QAction,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QMdiArea,
    QCheckBox,
)

from pyflow.blocks.executableblock import ExecutableBlock
from pyflow.core.executable import ExecutableState
from pyflow.graphics.widget import Widget
from pyflow.graphics.theme_manager import theme_manager

from pyflow.qss import loadStylesheets
from pyflow.qss import __file__ as QSS_INIT_PATH
from pyflow.scene.clipboard import BlocksClipboard
from pyflow.logging import log_init_time, get_logger

LOGGER = get_logger(__name__)
QSS_PATH = pathlib.Path(QSS_INIT_PATH).parent


class Window(QMainWindow):

    """Main window of the Pyflow Qt-based application."""

    @log_init_time(LOGGER)
    def __init__(self):
        super().__init__()

        self.stylesheets = [
            os.path.join(QSS_PATH, "pyflow.qss"),
            os.path.join(QSS_PATH, "pyflow_dark.qss"),
        ]
        loadStylesheets(self.stylesheets)

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

        # StatusBar
        self.statusbar = self.statusBar()

        self.updateMenus()

        # Window properties
        self.never_show_exit_prompt = False
        self.readSettings()
        self.show()

        # Block clipboard
        self.clipboard = BlocksClipboard()

    def createToolBars(self):
        """Does nothing, but is required by the QMainWindow interface."""

    def updateMenus(self):
        """Does nothing, but is required by the QMainWindow interface."""

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
            triggered=self.onFileSaveAsJupyter,
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
        self._actDuplicate = QAction(
            "&Duplicate",
            statusTip="Duplicate selected items",
            shortcut="Ctrl+D",
            triggered=self.onEditDuplicate,
        )
        self._actRun = QAction(
            "&Run",
            statusTip="Run the selected block",
            shortcut="Shift+Return",
            triggered=self.onEditRun,
        )

        # View
        self._actViewItems = QAction(
            "See All Blocks",
            statusTip="See all selected blocks. If none are selected, view all blocks",
            shortcut=" ",
            triggered=self.onMoveToItems,
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

        # Kernel
        self._actStartKernel = QAction(
            "&Start Kernel",
            self,
            statusTip="Start the kernel",
            triggered=self.start_kernel,
        )
        self._actInterruptKernel = QAction(
            "&Interrupt Kernel",
            self,
            statusTip="Interrupt the kernel",
            triggered=self.interrupt_kernel,
        )
        self._actStopKernel = QAction(
            "&Stop Kernel",
            self,
            statusTip="Stop the kernel",
            triggered=self.stop_kernel,
        )
        self._actRestartKernel = QAction(
            "&Restart Kernel",
            self,
            statusTip="Restart the kernel",
            triggered=self.restart_kernel,
        )

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
        self.editmenu.addAction(self._actDuplicate)
        self.editmenu.addAction(self._actRun)

        self.kernelMenu = self.menuBar().addMenu("&Kernel")
        self.kernelMenu.addAction(self._actStartKernel)
        self.kernelMenu.addAction(self._actInterruptKernel)
        self.kernelMenu.addAction(self._actStopKernel)
        self.kernelMenu.addAction(self._actRestartKernel)

        self.viewmenu = self.menuBar().addMenu("&View")
        self.thememenu = self.viewmenu.addMenu("Theme")
        self.thememenu.aboutToShow.connect(self.updateThemeMenu)
        self.viewmenu.addAction(self._actViewItems)

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

    def updateThemeMenu(self):
        """Update the theme selection menu."""
        self.thememenu.clear()
        theme_names = theme_manager().list_themes()
        for i, theme in enumerate(theme_names):
            action = self.thememenu.addAction(theme)
            action.setCheckable(True)
            action.setChecked(i == theme_manager().selected_theme_index)
            action.triggered.connect(self.themeMapper.map)
            self.themeMapper.setMapping(action, i)

    def updateWindowMenu(self):
        """Update the window menu."""
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
        _widget = Widget()
        if filename is not None:
            _widget.scene.load(filename)
            if filename.split(".")[-1] == "ipyg":
                _widget.savepath = filename
        return self.mdiArea.addSubWindow(_widget)

    def onFileNew(self):
        """Create a new file."""
        subwnd = self.createNewMdiChild()
        subwnd.show()

    def onFileOpen(self):
        """Open a file."""

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open ipygraph from file",
            "",
            "Interactive python graph or notebook (*.ipyg *.ipynb)",
        )

        if filename == "":
            return
        if os.path.isfile(filename):
            subwnd = self.createNewMdiChild(filename)
            subwnd.show()
            self.statusbar.showMessage(f"Loaded {filename}", 2000)

    def onFileSave(self) -> bool:
        """Save file.

        Returns:
            True if the file was successfully saved, False otherwise.

        """
        current_window = self.activeMdiChild()

        if current_window is not None:
            if current_window.savepath is None:
                return self.onFileSaveAs()
            self.saveWindow(current_window)
        return True

    def onFileSaveAs(self) -> bool:
        """Save file in a given directory, caching savepath for quick save.

        Returns:
            True if the file was successfully saved, False otherwise.

        """
        current_window = self.activeMdiChild()
        if current_window is not None:
            dialog = QFileDialog()
            dialog.setDefaultSuffix(".ipyg")
            filename, _ = dialog.getSaveFileName(
                self, "Save ipygraph to file", filter="IPython Graph (*.ipyg)"
            )
            if filename == "":
                return False
            current_window.savepath = filename

            # Note : the current_window is the activeMdiChild before the QFileDialog pops up
            self.saveWindow(current_window)
            return True
        return False

    def onFileSaveAsJupyter(self) -> bool:
        """Save file in a given directory as ipynb, caching savepath for quick save.

        Returns:
            True if the file was successfully saved, False otherwise.

        """
        current_window = self.activeMdiChild()
        if current_window is not None:
            dialog = QFileDialog()
            dialog.setDefaultSuffix(".ipynb")
            filename, _ = dialog.getSaveFileName(
                self, "Save ipygraph to file", filter="Jupyter Notebook (*.ipynb)"
            )
            if filename == "":
                return False
            current_window.saveAsJupyter(filename)
            success_msg = f"Saved as jupter notebook at {filename}"
            self.statusbar.showMessage(success_msg, 2000)
            LOGGER.info(success_msg)
            return True
        return False

    def saveWindow(self, window: Widget):
        """Save the given window."""
        window.save()
        success_msg = f"Saved ipygraph at {window.savepath}"
        self.statusbar.showMessage(success_msg, 2000)
        LOGGER.info(success_msg)

    @staticmethod
    def is_not_editing(current_window: Widget):
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
            self.clipboard.cut(current_window.scene)

    def onEditCopy(self):
        """Copy the selected items if not in edit mode."""
        current_window = self.activeMdiChild()
        if self.is_not_editing(current_window):
            self.clipboard.copy(current_window.scene)

    def onEditPaste(self):
        """Paste the selected items if not in edit mode."""
        current_window = self.activeMdiChild()
        if self.is_not_editing(current_window):
            self.clipboard.paste(current_window.scene)

    def onEditDelete(self):
        """Delete the selected items if not in edit mode."""
        current_window = self.activeMdiChild()
        if self.is_not_editing(current_window):
            current_window.view.deleteSelected()

    def onEditDuplicate(self):
        """Duplicate the selected items if not in edit mode."""
        current_window = self.activeMdiChild()
        if self.is_not_editing(current_window):
            self.clipboard.copy(current_window.scene)
            self.clipboard.paste(current_window.scene)

    def onEditRun(self):
        """Run the selected block if there is only one block selected."""
        current_window = self.activeMdiChild()
        selected_blocks, _ = current_window.scene.sortedSelectedItems()
        if len(selected_blocks) == 1:
            selected_blocks[0].run_left()

    def allWidgetsAreSaved(self):
        """Return true if all widgets are saved."""

        for widget in self.mdiArea.subWindowList():
            if isinstance(widget.widget(), Widget):
                if widget.widget().isModified():
                    return False

        return True

    def closeEvent(self, event: QCloseEvent):
        """Handle the event when the window is about to be closed."""

        if self.allWidgetsAreSaved() or self.never_show_exit_prompt:
            self.closeWindow(event)
            return

        # Show the exit without saving prompt
        quit_msg = "Exit without saving?"
        msgbox = QMessageBox(self)
        msgbox.setText(quit_msg)
        msgbox.setWindowTitle("Exit?")
        msgbox.addButton(QMessageBox.Yes)
        msgbox.addButton(QMessageBox.No)
        cb = QCheckBox("Never show this again")
        msgbox.setCheckBox(cb)
        msgbox.exec()

        if msgbox.checkBox().checkState() == Qt.CheckState.Checked:
            self.never_show_exit_prompt = True
            self.writeSettings()

        if msgbox.result() == int(str(QMessageBox.No)):
            event.ignore()
            return

        self.closeWindow(event)

    def closeWindow(self, event: QCloseEvent):
        """Close the window."""
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def activeMdiChild(self) -> Widget:
        """Get the active Widget if existing."""
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow is not None:
            return activeSubWindow.widget()
        return None

    def readSettings(self):
        """Read the settings from the config file."""
        settings = QSettings("Bycelium", "Pyflow")
        pos = settings.value("pos", QPoint(200, 200))
        size = settings.value("size", QSize(400, 400))
        self.move(pos)
        self.resize(size)
        if settings.value("isMaximized", False) == "true":
            self.showMaximized()
        if settings.value("NeverShowExitPrompt", False) == "true":
            self.never_show_exit_prompt = True
        LOGGER.info("Loaded settings under Bycelium/Pyflow")

    def writeSettings(self):
        """Write the settings to the config file."""
        settings = QSettings("Bycelium", "Pyflow")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())
        settings.setValue("isMaximized", self.isMaximized())
        settings.setValue("NeverShowExitPrompt", self.never_show_exit_prompt)
        LOGGER.info("Saved settings under Bycelium/Pyflow")

    def setActiveSubWindow(self, window):
        """Set the active subwindow to the given window."""
        if window:
            self.mdiArea.setActiveSubWindow(window)

    def onMoveToItems(self):
        """
        Ajust zoom and position to make the whole graph in the current window visible.
        If items are selected, then make all the selected items visible instead
        """
        current_window = self.activeMdiChild()
        if current_window is not None and isinstance(current_window, Widget):
            current_window.moveToItems()

    def setTheme(self, theme_index):
        """Set the theme of the application."""
        theme_manager().selected_theme_index = theme_index

    def start_kernel(self):
        """Start the kernel."""
        current_window = self._call_kernel("Kernel started")
        if current_window is not None:
            current_window.scene.kernel.start()

    def interrupt_kernel(self):
        """Interrupt the kernel."""
        current_window = self._call_kernel("Kernel interrupted")
        if current_window is not None:
            current_window.scene.kernel.interrupt()

    def stop_kernel(self):
        """Stop the kernel."""
        current_window = self._call_kernel("Kernel stopped")
        if current_window is not None:
            current_window.scene.kernel.stop()
            self.reset_block_states()

    def restart_kernel(self):
        """Restart the kernel."""
        current_window = self._call_kernel("Kernel restarted")
        if current_window is not None:
            current_window.scene.kernel.restart()
            self.reset_block_states()

    def _call_kernel(self, message):
        """Call a kernel function but check if a kernel exists first"""
        current_window = self.activeMdiChild()
        if current_window is not None:
            self.statusbar.showMessage(message)
            return current_window
        else:
            self.statusbar.showMessage("No active window")
            return None

    def reset_block_states(self):
        current_scene = self.activeMdiChild().scene
        for item in current_scene.items():
            if isinstance(item, ExecutableBlock):
                item.run_state = ExecutableState.IDLE
