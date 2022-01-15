# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

"""
Integration tests for the Blocks.
"""

import time
from typing import Callable
import pytest
import pyautogui
from pytestqt.qtbot import QtBot

from PyQt5.QtCore import QPointF
from pyflow.blocks.block import Block

from pyflow.blocks.codeblock import CodeBlock
from pyflow.blocks.markdownblock import MarkdownBlock

from tests.integration.utils import InAppTest, apply_function_inapp, CheckingQueue


class TestEditing(InAppTest):
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup reused variables."""
        self.start_app()
        self.code_block_1 = CodeBlock(title="Testing code block 1")
        self.code_block_2 = CodeBlock(title="Testing code block 2")
        self.widget.scene.addItem(self.code_block_1)
        self.widget.scene.addItem(self.code_block_2)

    def test_write_code_blocks(self, qtbot: QtBot):
        """code blocks can be written in."""

        block = self.code_block_1

        self.widget.scene.addItem(block)
        self.widget.view.horizontalScrollBar().setValue(block.x())
        self.widget.view.verticalScrollBar().setValue(
            block.y() - self.widget.view.height() + block.height
        )

        def testing_write(msgQueue: CheckingQueue):
            # click inside the block and write in it

            pos_block = self.get_global_pos(block, rel_pos=(0.5, 0.5))

            pyautogui.moveTo(pos_block.x(), pos_block.y())
            pyautogui.click()
            pyautogui.press(["a", "b", "enter", "a"])

            time.sleep(0.1)

            msgQueue.check_equal(
                block.source_editor.text().replace("\r", ""),
                "ab\na",
                "The chars have been written properly",
            )

            with pyautogui.hold("ctrl"):
                pyautogui.press("z")

            msgQueue.check_equal(
                block.source_editor.text().replace("\r", ""),
                "ab\n",
                "undo worked properly",
            )

            with pyautogui.hold("ctrl"):
                pyautogui.press("y")

            time.sleep(0.1)

            msgQueue.check_equal(
                block.source_editor.text().replace("\r", ""),
                "ab\na",
                "redo worked properly",
            )

            time.sleep(0.1)

            msgQueue.stop()

        apply_function_inapp(self.window, testing_write)

    def test_editing_history(self, qtbot: QtBot):
        """code blocks keep their own undo history."""
        self.code_block_1.setY(-200)
        self.code_block_2.setY(200)

        def testing_history(msgQueue: CheckingQueue):
            # click inside the block and write in it
            initial_pos = (self.code_block_2.pos().x(), self.code_block_2.pos().y())
            pos_block_2 = self.get_global_pos(self.code_block_2, rel_pos=(0.5, 0.05))
            center_block_1 = self.get_global_pos(self.code_block_1, rel_pos=(0.5, 0.5))
            center_block_2 = self.get_global_pos(self.code_block_2, rel_pos=(0.5, 0.5))

            pyautogui.moveTo(center_block_1.x(), center_block_1.y())
            pyautogui.click()
            pyautogui.press(["a", "b", "enter", "a"])

            pyautogui.moveTo(center_block_2.x(), center_block_2.y())
            pyautogui.click()
            pyautogui.press(["c", "d", "enter", "d"])

            pyautogui.moveTo(pos_block_2.x(), pos_block_2.y())
            pyautogui.mouseDown(button="left")
            pyautogui.moveTo(pos_block_2.x(), int(1.2 * pos_block_2.y()))
            pyautogui.mouseUp(button="left")

            pyautogui.moveTo(center_block_1.x(), center_block_1.y())
            pyautogui.click()
            with pyautogui.hold("ctrl"):
                pyautogui.press("z")

            time.sleep(0.1)

            # Undo in the 1st edited block should only undo in that block
            msgQueue.check_equal(
                self.code_block_1.source_editor.text().replace("\r", ""),
                "ab\n",
                "Undone selected editing",
            )

            pyautogui.moveTo(pos_block_2.x(), pos_block_2.y())
            pyautogui.click()
            with pyautogui.hold("ctrl"):
                pyautogui.press("z", presses=3, interval=0.1)

            time.sleep(0.1)

            msgQueue.check_equal(
                (self.code_block_2.pos().x(), self.code_block_2.pos().y()),
                initial_pos,
                "Undone graph",
            )

            msgQueue.check_equal(
                self.code_block_1.source_editor.text().replace("\r", ""),
                "cd\nd",
                "Not undone editing",
            )

            msgQueue.stop()

        apply_function_inapp(self.window, testing_history)

    def test_finish(self):
        self.window.close()
