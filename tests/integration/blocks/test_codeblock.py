# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Integration tests for the OCBCodeBlocks.
"""

import pyautogui
import pytest
from pytestqt.qtbot import QtBot

from PyQt5.QtCore import QPointF

from opencodeblocks.graphics.blocks.codeblock import OCBCodeBlock
from opencodeblocks.graphics.window import OCBWindow
from opencodeblocks.graphics.widget import OCBWidget

from tests.integration.utils import apply_function_inapp, CheckingQueue


class TestCodeBlocks:

    @pytest.fixture(autouse=True)
    def setup(self):
        """ Setup reused variables. """
        self.window = OCBWindow()
        self.ocb_widget = OCBWidget()
        self.subwindow = self.window.mdiArea.addSubWindow(self.ocb_widget)
        self.subwindow.show()

    def test_run_python(self, qtbot: QtBot):
        """ run source code when run button is pressed. """

        # Add a block with the source to the window
        EXPRESSION = "3 + 5 * 2"
        SOURCE_TEST = f'''print({EXPRESSION})'''
        expected_result = str(3 + 5 * 2)

        test_block = OCBCodeBlock(title="CodeBlock test", source=SOURCE_TEST)
        self.ocb_widget.scene.addItem(test_block)

        def testing_run(msgQueue: CheckingQueue):

            msgQueue.check_equal(test_block.stdout.strip(), "")

            pos_run_button = test_block.run_button.pos()
            pos_run_button = QPointF(
                pos_run_button.x() + test_block.run_button.width() / 2,
                pos_run_button.y() + test_block.run_button.height() / 2,
            )
            pos_run_button = self.ocb_widget.view.mapFromScene(pos_run_button)
            pos_run_button = self.ocb_widget.view.mapToGlobal(pos_run_button)

            # Run the block by pressung the run button
            pyautogui.moveTo(pos_run_button.x(), pos_run_button.y())
            pyautogui.mouseDown(button="left")
            pyautogui.mouseUp(button="left")

            # qtbot.mouseMove(test_block.run_button)
            # qtbot.mousePress(test_block.run_button,
            #                  Qt.MouseButton.LeftButton, delay=1)
            # qtbot.mouseRelease(test_block.run_button, Qt.MouseButton.LeftButton)

            # When the execution becomes non-blocking for the UI, a refactor will be needed here.
            msgQueue.check_equal(test_block.stdout.strip(), expected_result)
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)
