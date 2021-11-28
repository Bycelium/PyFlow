# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Integration tests for the OCBBlocks.
"""

import pytest
import pyautogui
from pytestqt.qtbot import QtBot

from PyQt5.QtCore import QPointF

from opencodeblocks.graphics.blocks.codeblock import OCBBlock
from opencodeblocks.graphics.window import OCBWindow
from opencodeblocks.graphics.widget import OCBWidget

from tests.integration.utils import apply_function_inapp, CheckingQueue


class TestBlocks:

    @pytest.fixture(autouse=True)
    def setup(self):
        """ Setup reused variables. """
        self.window = OCBWindow()
        self.ocb_widget = OCBWidget()
        self.subwindow = self.window.mdiArea.addSubWindow(self.ocb_widget)
        self.subwindow.show()

        self.block1 = OCBBlock(title="Testing block 1")
        self.block2 = OCBBlock(title="Testing block 2")

    def test_create_blocks(self, qtbot: QtBot):
        """ can be added to the scene. """
        self.ocb_widget.scene.addItem(self.block1)

    def test_move_blocks(self, qtbot: QtBot):
        """ can be dragged around with the mouse. """
        self.ocb_widget.scene.addItem(self.block1)

        def testing_drag(msgQueue: CheckingQueue):
            expected_move_amount = [70, -30]
            pos_block = QPointF(self.block1.pos().x(), self.block1.pos().y())

            pos_block.setX(
                pos_block.x() + self.block1.title_height + self.block1.edge_size
            )
            pos_block.setY(pos_block.y() + self.block1.title_height/2)

            pos_block = self.ocb_widget.view.mapFromScene(pos_block)
            pos_block = self.ocb_widget.view.mapToGlobal(pos_block)

            pyautogui.moveTo(pos_block.x(), pos_block.y())
            pyautogui.mouseDown(button="left")

            iterations = 5
            for i in range(iterations+1):
                pyautogui.moveTo(
                    pos_block.x() + expected_move_amount[0] * i / iterations,
                    pos_block.y() + expected_move_amount[1] * i / iterations
                )

            pyautogui.mouseUp(button="left")

            move_amount = [self.block1.pos().x(), self.block1.pos().y()]
            # rectify because the scene can be zoomed :
            move_amount[0] = move_amount[0] * self.ocb_widget.view.zoom
            move_amount[1] = move_amount[1] * self.ocb_widget.view.zoom

            msgQueue.check_equal(
                move_amount, expected_move_amount, "Block moved by the correct amound")
            msgQueue.stop()

        apply_function_inapp(self.window, testing_drag)
