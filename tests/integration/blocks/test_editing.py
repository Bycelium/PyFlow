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

from tests.integration.utils import apply_function_inapp, CheckingQueue, start_app


class TestEditing:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup reused variables."""
        start_app(self)
        self.code_block = CodeBlock(title="Testing code block 1")
        self.code_block_2 = CodeBlock(title="Testing code block 2")

    def test_history_not_lost(self, qtbot: QtBot):
        """code blocks keep their own undo history."""

        self._widget.scene.addItem(self.code_block)
        self._widget.scene.addItem(self.code_block_2)
        self.code_block.setY(200)
        self.code_block_2.setY(-200)

        def testing_history(msgQueue: CheckingQueue):
            # click inside the block and write in it

            pos_block_1 = QPointF(self.code_block.pos().x(), self.code_block.pos().y())
            pos_block_2 = QPointF(
                self.code_block_2.pos().x(), self.code_block_2.pos().y()
            )

            pos_block_1.setX(self.code_block.x() + self.code_block.width / 2)
            pos_block_1.setY(self.code_block.y() + self.code_block.height / 2)

            pos_block_2.setX(self.code_block_2.x() + self.code_block_2.width / 2)
            pos_block_2.setY(self.code_block_2.y() + self.code_block_2.height / 2)

            pos_block_1 = self._widget.view.mapFromScene(pos_block_1)
            pos_block_1 = self._widget.view.mapToGlobal(pos_block_1)

            pos_block_2 = self._widget.view.mapFromScene(pos_block_2)
            pos_block_2 = self._widget.view.mapToGlobal(pos_block_2)

            pyautogui.moveTo(pos_block_1.x(), pos_block_1.y())
            pyautogui.click()
            pyautogui.press(["a", "b", "enter", "a"])

            pyautogui.moveTo(pos_block_2.x(), pos_block_2.y())
            pyautogui.click()
            pyautogui.press(["c", "d", "enter", "d"])

            pyautogui.moveTo(pos_block_1.x(), pos_block_1.y())
            pyautogui.click()
            with pyautogui.hold("ctrl"):
                pyautogui.press("z")

            time.sleep(0.1)

            msgQueue.check_equal(
                self.code_block.source_editor.text().replace("\r", ""),
                "ab\n",
                "undo done properly",
            )

            pyautogui.moveTo(pos_block_2.x(), pos_block_2.y())
            pyautogui.click()
            with pyautogui.hold("ctrl"):
                pyautogui.press("z")

            time.sleep(0.1)

            msgQueue.check_equal(
                self.code_block_2.source_editor.text().replace("\r", ""),
                "cd\n",
                "undo done properly",
            )
            time.sleep(0.1)

            msgQueue.stop()

        apply_function_inapp(self.window, testing_history)

    def test_write_code_blocks(self, qtbot: QtBot):
        """code blocks can be written in."""

        block = self.code_block

        self._widget.scene.addItem(block)
        self._widget.view.horizontalScrollBar().setValue(block.x())
        self._widget.view.verticalScrollBar().setValue(
            block.y() - self._widget.view.height() + block.height
        )

        def testing_write(msgQueue: CheckingQueue):
            # click inside the block and write in it

            pos_block = QPointF(block.pos().x(), block.pos().y())

            pos_block.setX(pos_block.x() + block.width / 2)
            pos_block.setY(pos_block.y() + block.height / 2)

            pos_block = self._widget.view.mapFromScene(pos_block)
            pos_block = self._widget.view.mapToGlobal(pos_block)

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

    def test_finish(self):
        self.window.close()
