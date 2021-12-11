# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Integration tests for the OCBBlocks.
"""

import pytest
import pyautogui
from pytestqt.qtbot import QtBot

from PyQt5.QtCore import QPointF

from opencodeblocks.blocks.block import OCBBlock

from tests.integration.utils import apply_function_inapp, CheckingQueue, start_app


class TestBlocks:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup reused variables."""
        start_app(self)
        self.block = OCBBlock(title="Testing block")

    def test_create_blocks(self, qtbot: QtBot):
        """can be added to the scene."""
        self.ocb_widget.scene.addItem(self.block)

    def test_move_blocks(self, qtbot: QtBot):
        """can be dragged around with the mouse."""
        self.ocb_widget.scene.addItem(self.block)
        self.ocb_widget.view.horizontalScrollBar().setValue(self.block.x())
        self.ocb_widget.view.verticalScrollBar().setValue(
            self.block.y() - self.ocb_widget.view.height() + self.block.height
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

            pos_block = self.ocb_widget.view.mapFromScene(pos_block)
            pos_block = self.ocb_widget.view.mapToGlobal(pos_block)

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
            move_amount[0] = move_amount[0] * self.ocb_widget.view.zoom
            move_amount[1] = move_amount[1] * self.ocb_widget.view.zoom

            msgQueue.check_equal(
                move_amount, expected_move_amount, "Block moved by the correct amound"
            )
            msgQueue.stop()

        apply_function_inapp(self.window, testing_drag)
