# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

"""
Integration tests for the Blocks.
"""

import pytest
import pyautogui
from pytestqt.qtbot import QtBot

from pyflow.blocks.block import Block

from tests.integration.utils import apply_function_inapp, CheckingQueue, InAppTest


class TestBlocks(InAppTest):
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup reused variables."""
        self.start_app()
        self.block = Block(title="Testing block")

    def test_create_blocks(self, qtbot: QtBot):
        """can be added to the scene."""
        self.widget.scene.addItem(self.block)

    def test_move_blocks(self, qtbot: QtBot):
        """can be dragged around with the mouse."""
        self.widget.scene.addItem(self.block)
        self.widget.view.horizontalScrollBar().setValue(int(self.block.x()))
        self.widget.view.verticalScrollBar().setValue(
            int(self.block.y() - self.widget.view.height() + self.block.height)
        )

        def testing_drag(msgQueue: CheckingQueue):
            # put block1 at the bottom left
            # This line works because the zoom is 1 by default.

            expected_move_amount = [20, -30]
            pos_block = self.get_global_pos(self.block, rel_pos=(0.05, 0.5))

            pyautogui.moveTo(pos_block.x(), pos_block.y())
            pyautogui.mouseDown(button="left")

            iterations = 5
            for i in range(iterations + 1):
                pyautogui.moveTo(
                    pos_block.x() + expected_move_amount[0] * i / iterations,
                    pos_block.y() + expected_move_amount[1] * i / iterations,
                )

            pyautogui.mouseUp(button="left")

            move_amount = [self.block.pos().x(), self.block.pos().y()]
            # rectify because the scene can be zoomed :
            move_amount[0] = move_amount[0] * self.widget.view.zoom
            move_amount[1] = move_amount[1] * self.widget.view.zoom

            msgQueue.check_equal(
                move_amount, expected_move_amount, "Block moved by the correct amound"
            )
            msgQueue.stop()

        apply_function_inapp(self.window, testing_drag)

    def test_finish(self):
        self.window.close()
