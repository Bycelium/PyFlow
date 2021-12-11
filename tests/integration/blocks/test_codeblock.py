# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Integration tests for the OCBCodeBlocks.
"""

import time
import pyautogui
import pytest

from PyQt5.QtCore import QPointF

from opencodeblocks.blocks.codeblock import OCBCodeBlock

from tests.integration.utils import apply_function_inapp, CheckingQueue, start_app


class TestCodeBlocks():

    @pytest.fixture(autouse=True)
    def setup(self):
        """ Setup reused variables. """
        start_app(self)

    def test_run_python(self):
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

            time.sleep(0.5)

            msgQueue.check_equal(test_block.stdout.strip(), expected_result)
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)
