# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Integration tests for the execution flow.
"""

import pytest
import time

from pyflow.blocks.codeblock import CodeBlock

from tests.integration.utils import apply_function_inapp, CheckingQueue, start_app


class TestCodeBlocksFlow:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup reused variables."""
        start_app(self)

        self._widget.scene.load("tests/assets/flow_test.ipyg")

        self.titles = [
            "Test flow 5",
            "Test flow 4",
            "Test no connection 1",
            "Test input only 2",
            "Test output only 1",
        ]
        self.blocks_to_run = [None] * 5
        for item in self._widget.scene.items():
            if isinstance(item, CodeBlock):
                if item.title in self.titles:
                    self.blocks_to_run[self.titles.index(item.title)] = item

    def test_duplicated_run(self):
        """run exactly one time pressing run right."""
        for b in self.blocks_to_run:
            b.stdout = ""

        def testing_no_duplicates(msgQueue: CheckingQueue):

            block_to_run: CodeBlock = self.blocks_to_run[0]

            def run_block():
                block_to_run.run_right()

            msgQueue.run_lambda(run_block)
            time.sleep((block_to_run.transmitting_duration / 1000) + 0.2)
            while block_to_run.run_state != 0:
                time.sleep(0.1)

            # 6 and not 6\n6
            msgQueue.check_equal(block_to_run.stdout.strip(), "6")
            msgQueue.stop()

        apply_function_inapp(self.window, testing_no_duplicates)

    def test_flow_left(self):
        """run its dependencies when pressing left run."""

        for b in self.blocks_to_run:
            b.stdout = ""

        def testing_run(msgQueue: CheckingQueue):

            block_to_run: CodeBlock = self.blocks_to_run[0]
            block_to_not_run: CodeBlock = self.blocks_to_run[1]

            def run_block():
                block_to_run.run_left()

            msgQueue.run_lambda(run_block)
            time.sleep((block_to_run.transmitting_duration / 1000) + 0.2)
            while block_to_run.run_state != 0:
                time.sleep(0.1)

            msgQueue.check_equal(block_to_run.stdout.strip(), "6")
            msgQueue.check_equal(block_to_not_run.stdout.strip(), "")
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)

    def test_no_connection_left(self):
        """run itself only when has no dependecy and pressing left run."""

        def testing_run(msgQueue: CheckingQueue):

            block_to_run: CodeBlock = self.blocks_to_run[
                self.titles.index("Test no connection 1")
            ]

            def run_block():
                block_to_run.run_left()

            print("About to run !")

            msgQueue.run_lambda(run_block)
            time.sleep((block_to_run.transmitting_duration / 1000) + 0.2)
            while block_to_run.run_state != 0:
                time.sleep(0.1)

            msgQueue.check_equal(block_to_run.stdout.strip(), "1")
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)

    def test_no_connection_right(self):
        """run itself only when is not a dependecy and pressing right run."""

        def testing_run(msgQueue: CheckingQueue):

            block_to_run: CodeBlock = self.blocks_to_run[
                self.titles.index("Test no connection 1")
            ]

            def run_block():
                block_to_run.run_right()

            msgQueue.run_lambda(run_block)
            time.sleep((block_to_run.transmitting_duration / 1000) + 0.2)
            while block_to_run.run_state != 0:
                time.sleep(0.1)

            # Just check that it doesn't crash
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)

    def test_finish(self):
        self.window.close()
