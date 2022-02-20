# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

"""
Integration tests for the CodeBlocks.
"""

import time
import os
import pyautogui
import pytest

from pyflow.blocks.codeblock import CodeBlock
from pyflow.blocks.executableblock import ExecutableState

from tests.integration.utils import apply_function_inapp, CheckingQueue, InAppTest


class TestCodeBlocks(InAppTest):
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup reused variables."""
        self.start_app()

    def test_run_python(self):
        """run source code when run button is pressed."""

        # Add a block with the source to the window
        EXPRESSION = "3 + 5 * 2"
        SOURCE_TEST = f"""print({EXPRESSION})"""
        expected_result = str(3 + 5 * 2)

        test_block = CodeBlock(title="CodeBlock test", source=SOURCE_TEST)
        self.widget.scene.addItem(test_block)

        def testing_run(msgQueue: CheckingQueue):

            msgQueue.check_equal(test_block.stdout.strip(), "")
            pos_run_button = self.get_global_pos(
                test_block.run_button, rel_pos=(0.5, 0.5)
            )

            # Run the block by pressung the run button
            pyautogui.moveTo(pos_run_button.x(), pos_run_button.y())
            pyautogui.mouseDown(button="left")
            pyautogui.mouseUp(button="left")

            time.sleep((test_block.transmitting_duration / 1000) + 0.2)
            while test_block.run_state != ExecutableState.DONE:
                time.sleep(0.1)

            msgQueue.check_equal(test_block.stdout.strip(), expected_result)
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)

    def test_run_block_with_path(self):
        """runs blocks with the correct working directory for the kernel."""
        file_example_path = "./tests/assets/example_graph1.ipyg"
        asset_path = "./tests/assets/data.txt"
        self.widget.scene.load(os.path.abspath(file_example_path))

        def testing_path(msgQueue: CheckingQueue):
            block_of_test: CodeBlock = None
            for item in self.widget.scene.items():
                if isinstance(item, CodeBlock) and item.title == "test1":
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
            while block_of_test.run_state != ExecutableState.DONE:
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
