# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Integration tests for the OCBCodeBlocks.
"""

import pyautogui
import pytest
from pytestqt.qtbot import QtBot

import time

from PyQt5.QtCore import QPointF

from opencodeblocks.blocks.codeblock import OCBCodeBlock
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

        self.ocb_widget.scene.load("tests/assets/flow_test.ipyg")

        titles = ["Test flow 5", "Test flow 4", "Test no connection 1",
                  "Test input only 2", "Test output only 1"]
        self.blocks_to_run = [None]*5
        for item in self.ocb_widget.scene.items():
            if isinstance(item, OCBCodeBlock):
                if item.title in titles:
                    self.blocks_to_run[titles.index(item.title)] = item

    def test_flow_left(self, qtbot: QtBot):
        """ Correct flow when pressing left run """

        def testing_run(msgQueue: CheckingQueue):

            block_to_run: OCBCodeBlock = self.blocks_to_run[0]
            block_to_not_run: OCBCodeBlock = self.blocks_to_run[1]

            def run_block():
                block_to_run.run_left()

            msgQueue.run_lambda(run_block)
            time.sleep(1)

            msgQueue.check_equal(block_to_run.stdout.strip(), "6")
            msgQueue.check_equal(block_to_not_run.stdout.strip(), "")
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)
