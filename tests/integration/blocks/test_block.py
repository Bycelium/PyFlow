# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

"""
Integration tests for the Blocks.
"""

import pytest
import pyautogui
from pytestqt.qtbot import QtBot

from PyQt5.QtCore import QPointF

from pyflow.blocks.block import Block

from tests.integration.utils import apply_function_inapp, CheckingQueue, start_app


class TestBlocks:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup reused variables."""
        start_app(self)
        self.block = Block(title="Testing block")

    def test_create_blocks(self, qtbot: QtBot):
        """can be added to the scene."""
        self._widget.scene.addItem(self.block)

    def test_move_blocks(self, qtbot: QtBot):
        """can be dragged around with the mouse."""
        self._widget.scene.addItem(self.block)
        self._widget.view.horizontalScrollBar().setValue(self.block.x())
        self._widget.view.verticalScrollBar().setValue(
            self.block.y() - self._widget.view.height() + self.block.height
        )

        def testing_drag(msgQueue: CheckingQueue):
            # put block1 at the bottom left
            # This line works because the zoom is 1 by default.

            expected_move_amount = [20, -30]
            pos_block = QPointF(self.block.pos().x(), self.block.pos().y())

            pos_block.setX(
                pos_block.x() + self.block.title_widget.height() + self.block.edge_size
            )
            pos_block.setY(pos_block.y() + self.block.title_widget.height() / 2)

            pos_block = self._widget.view.mapFromScene(pos_block)
            pos_block = self._widget.view.mapToGlobal(pos_block)

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
            move_amount[0] = move_amount[0] * self._widget.view.zoom
            move_amount[1] = move_amount[1] * self._widget.view.zoom

            msgQueue.check_equal(
                move_amount, expected_move_amount, "Block moved by the correct amound"
            )
            msgQueue.stop()

        apply_function_inapp(self.window, testing_drag)

    def test_finish(self):
        self.window.close()
