# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Integration tests for the OCBCodeBlocks.
"""

import pytest
import time

from opencodeblocks.blocks.codeblock import OCBCodeBlock
from opencodeblocks.graphics.window import OCBWindow
from opencodeblocks.graphics.widget import OCBWidget

from tests.integration.utils import apply_function_inapp, CheckingQueue


class TestCodeBlocks:
    """Test the execution flow"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup reused variables."""
        self.window = OCBWindow()
        self.ocb_widget = OCBWidget()
        self.subwindow = self.window.mdiArea.addSubWindow(self.ocb_widget)
        self.subwindow.show()

        self.ocb_widget.scene.load("tests/assets/flow_test.ipyg")

        self.titles = [
            "Test flow 5",
            "Test flow 4",
            "Test flow 8",
            "Test no connection 1",
        ]
        self.blocks_to_run = [None] * len(self.titles)
        for item in self.ocb_widget.scene.items():
            if isinstance(item, OCBCodeBlock):
                if item.title in self.titles:
                    self.blocks_to_run[self.titles.index(item.title)] = item

    def test_flow_left(self):
        """Correct flow when pressing left run"""

        def testing_run(msgQueue: CheckingQueue):

            block_to_run: OCBCodeBlock = self.blocks_to_run[
                self.titles.index("Test flow 5")
            ]
            block_to_not_run: OCBCodeBlock = self.blocks_to_run[
                self.titles.index("Test flow 4")
            ]

            def run_block():
                block_to_run.run_left()

            # Run the execution in a separate thread
            # to give time for the outputs to show before checking them
            msgQueue.run_lambda(run_block)
            time.sleep(0.5)

            msgQueue.check_equal(block_to_run.stdout.strip(), "6")
            msgQueue.check_equal(block_to_not_run.stdout.strip(), "")
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)

    def test_flow_right(self):
        """Correct flow when pressing right run"""

        def testing_run(msgQueue: CheckingQueue):

            block_to_run: OCBCodeBlock = self.blocks_to_run[
                self.titles.index("Test flow 5")
            ]
            block_output: OCBCodeBlock = self.blocks_to_run[
                self.titles.index("Test flow 8")
            ]
            block_to_not_run: OCBCodeBlock = self.blocks_to_run[
                self.titles.index("Test flow 4")
            ]

            def run_block():
                block_to_run.run_right()

            msgQueue.run_lambda(run_block)
            time.sleep(0.5)

            msgQueue.check_equal(block_output.stdout.strip(), "21")
            msgQueue.check_equal(block_to_not_run.stdout.strip(), "")
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)

    def test_no_connection_left(self):
        """Run_left when no connection"""

        def testing_run(msgQueue: CheckingQueue):

            block_to_run: OCBCodeBlock = self.blocks_to_run[
                self.titles.index("Test no connection 1")
            ]

            def run_block():
                block_to_run.run_left()

            msgQueue.run_lambda(run_block)
            time.sleep(0.5)

            msgQueue.check_equal(block_to_run.stdout.strip(), "1")
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)

    def test_no_connection_right(self):
        """Run_right when no connection"""

        def testing_run(msgQueue: CheckingQueue):

            block_to_run: OCBCodeBlock = self.blocks_to_run[
                self.titles.index("Test no connection 1")
            ]

            def run_block():
                block_to_run.run_right()

            msgQueue.run_lambda(run_block)
            time.sleep(0.5)

            # Just check that it doesn't crash
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)
