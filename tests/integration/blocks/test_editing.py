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

from pyflow.blocks.codeblock import CodeBlock
from pyflow.blocks.markdownblock import MarkdownBlock

from tests.integration.utils import apply_function_inapp, CheckingQueue, start_app


class TestEditing:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup reused variables."""
        start_app(self)
        self.code_block = CodeBlock(title="Testing block")
        self.markdown_block = MarkdownBlock(title="Testing block")

    def test_write_code_blocks(self, qtbot: QtBot):
        """code blocks can be written in."""

        test_write_in(self, self.code_block, qtbot)

    def test_write_markdown_blocks(self, qtbot: QtBot):
        """code blocks can be written in."""

        test_write_in(self, self.markdown_block, qtbot)


def test_write_in(self: TestEditing, block: Block, qtbot: QtBot):
    def test_write(self, qtbot: QtBot):
        """can be written in."""
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
            pyautogui.mouseDown(button="left")
            pyautogui.mouseUp(button="left")
            pyautogui.press(key="a")
            pyautogui.press(key="b")
            pyautogui.press(key="enter")
            pyautogui.press(key="a")

            msgQueue.check_equal(
                block.source_editor.text(),
                "ab\na",
                "The chars have been written properly",
            )
            with pyautogui.hold("ctrl"):
                pyautogui.press(key="z")

            msgQueue.check_equal(
                block.source_editor.text(),
                "ab",
                "undo worked properly",
            )

            with pyautogui.hold("ctrl"):
                pyautogui.press(key="z")

            msgQueue.check_equal(
                block.source_editor.text(),
                "ab\na",
                "redo worked properly",
            )

            msgQueue.stop()

        apply_function_inapp(self.window, testing_write)
