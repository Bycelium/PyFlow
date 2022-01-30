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

    # def test_write_code_blocks(self, qtbot: QtBot):
    #     """source of code blocks can be written using editor."""

    #     def testing_write(msgQueue: CheckingQueue):
    #         # click inside the block and write in it
    #         center_block = self.get_global_pos(self.code_block_1, rel_pos=(0.5, 0.5))
    #         pyautogui.moveTo(center_block.x(), center_block.y())
    #         pyautogui.click()
    #         pyautogui.press(["a", "b", "enter", "a"])

    #         # click outside the block to update source
    #         corner_block = self.get_global_pos(self.code_block_1, rel_pos=(-0.1, -0.1))
    #         pyautogui.moveTo(corner_block.x(), corner_block.y())
    #         pyautogui.click()

    #         msgQueue.check_equal(
    #             self.code_block_1.source.replace("\r", ""),
    #             "ab\na",
    #             "The chars have been written properly",
    #         )
    #         msgQueue.stop()

    #     apply_function_inapp(self.window, testing_write)

    # def test_code_blocks_history(self, qtbot: QtBot):
    #     """code blocks source have their own history (undo/redo)."""

    #     def testing_history(msgQueue: CheckingQueue):
    #         pos_block = self.get_global_pos(self.code_block_1, rel_pos=(0.5, 0.5))

    #         pyautogui.moveTo(pos_block.x(), pos_block.y())
    #         pyautogui.click()
    #         pyautogui.press(["a", "b", "enter", "a"])

    #         msgQueue.check_equal(
    #             self.code_block_1.source_editor.text().replace("\r", ""),
    #             "ab\na",
    #             "The chars have been written properly",
    #         )

    #         with pyautogui.hold("ctrl"):
    #             pyautogui.press("z")

    #         msgQueue.check_equal(
    #             self.code_block_1.source_editor.text().replace("\r", ""),
    #             "ab\n",
    #             "undo worked properly",
    #         )

    #         with pyautogui.hold("ctrl"):
    #             pyautogui.press("y")

    #         msgQueue.check_equal(
    #             self.code_block_1.source_editor.text().replace("\r", ""),
    #             "ab\na",
    #             "redo worked properly",
    #         )

    #         msgQueue.stop()

    #     apply_function_inapp(self.window, testing_history)

    def test_editing_history(self, qtbot: QtBot):
        """code blocks history is compatible with scene history."""
        self.code_block_1.setY(-200)
        self.code_block_2.setY(200)

        code_block_1_id = self.code_block_1.id
        code_block_2_id = self.code_block_2.id

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
            pyautogui.moveTo(pos_block_2.x(), int(0.9 * pos_block_2.y()))
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

            pyautogui.moveTo(pos_block_2.x(), int(0.75 * pos_block_2.y()))
            pyautogui.click()
            with pyautogui.hold("ctrl"):
                pyautogui.press("z", presses=2, interval=0.1)

            time.sleep(0.1)
            # Need to relink after re-serialization
            code_block_1: CodeBlock = self.widget.scene.getItemById(code_block_1_id)
            code_block_2: CodeBlock = self.widget.scene.getItemById(code_block_2_id)

            msgQueue.check_equal(
                code_block_1.source_editor.text().replace("\r", ""),
                "ab\na",
                "Undone previous editing",
            )
            msgQueue.check_equal(
                (code_block_2.pos().x(), code_block_2.pos().y()),
                initial_pos,
                "Undone graph modification",
            )
            msgQueue.check_equal(
                code_block_2.source_editor.text().replace("\r", ""),
                "cd\nd",
                "Not undone 2 times previous editing",
            )

            msgQueue.stop()

        apply_function_inapp(self.window, testing_history)
