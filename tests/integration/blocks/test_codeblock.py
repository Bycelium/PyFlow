# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Integration tests for the OCBCodeBlocks.
"""

import time
import os
import pyautogui
import pytest

from PyQt5.QtCore import QPointF

from opencodeblocks.blocks.codeblock import OCBCodeBlock

from tests.integration.utils import apply_function_inapp, CheckingQueue, start_app


class TestCodeBlocks:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup reused variables."""
        start_app(self)

    def test_run_python(self):
        """run source code when run button is pressed."""

        # Add a block with the source to the window
        EXPRESSION = "3 + 5 * 2"
        SOURCE_TEST = f"""print({EXPRESSION})"""
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

    def test_run_block_with_path(self):
        """runs blocks with the correct working directory for the kernel"""
        file_example_path = "./tests/assets/example_graph1.ipyg"
        asset_path = "./tests/assets/data.txt"
        self.ocb_widget.scene.load(os.path.abspath(file_example_path))

        def testing_path(msgQueue: CheckingQueue):
            block_of_test: OCBCodeBlock = None
            for item in self.ocb_widget.scene.items():
                if isinstance(item, OCBCodeBlock) and item.title == "test1":
                    block_of_test = item
                    break
            msgQueue.check_equal(
                block_of_test is not None,
                True,
                "example_graph1 contains a block titled test1",
            )

            def run_block():
                block_of_test.run_code()

            msgQueue.run_lambda(run_block)
            time.sleep(0.1)  # wait for the lambda to complete.
            while block_of_test.run_color != 0:
                time.sleep(0.1)  # wait for the execution to finish.

            time.sleep(0.1)

            file_content = open(asset_path).read()

            msgQueue.check_equal(
                block_of_test.stdout.strip(),
                file_content,
                "The asset file is read properly",
            )

            msgQueue.stop()

        apply_function_inapp(self.window, testing_path)

    def test_finish(self):
        self.window.close()
