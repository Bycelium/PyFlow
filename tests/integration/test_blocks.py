# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Integration tests for the OCBBlocks.
"""

# Imports needed for testing
import threading
import queue
import pytest
from pytest_mock import MockerFixture
import pytest_check as check
import pyautogui

# Packages tested
from opencodeblocks.graphics.blocks.codeblock import OCBCodeBlock
from opencodeblocks.graphics.window import OCBWindow
from opencodeblocks.graphics.widget import OCBWidget

from qtpy.QtWidgets import QApplication
from PyQt5.QtCore import QPointF


class TestBlocks:

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        """ Setup reused variables. """
        self.window = OCBWindow()
        self.ocb_widget = OCBWidget()
        self.subwindow = self.window.mdiArea.addSubWindow(self.ocb_widget)

        self.block1 = OCBCodeBlock(title="Testing block 1", source="print(1)")
        self.block2 = OCBCodeBlock(title="Testing block 2", source="print(2)")

    def test_create_blocks(self, qtbot):
        """ can be added to the scene. """
        self.ocb_widget.scene.addItem(self.block1)

    def test_move_blocks(self, qtbot):
        """ can be dragged around with the mouse. """
        self.ocb_widget.scene.addItem(self.block1)
        self.subwindow.show()

        QApplication.processEvents()

        expected_move_amount = [70, -30]
        STOP_MSG = "stop"
        CHECK_MSG = "check"

        msgQueue = queue.Queue()

        def testing_drag(msgQueue):
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

            msgQueue.put([
                CHECK_MSG,
                move_amount,
                expected_move_amount,
                "Block moved by the correct amound"
            ])

            msgQueue.put([STOP_MSG])

        t = threading.Thread(target=testing_drag, args=(msgQueue,))
        t.start()

        while True:
            QApplication.processEvents()
            if not msgQueue.empty():
                msg = msgQueue.get()
                if msg[0] == STOP_MSG:
                    break
                elif msg[0] == CHECK_MSG:
                    check.equal(msg[1], msg[2], msg[3])
        t.join()
        self.window.close()


"""
def test_running_python(qtbot):
    # The blocks should run arbitrary python when unfocused
    wnd = OCBWindow()
    
    EXPRESSION = "3 + 5 * 2"
    SOURCE_TEST = \
        '''
            print(%s)
        ''' % EXPRESSION
    expected_result = str(eval(EXPRESSION))

    # Let's add a block with the source to the window !
    ocb_widget = OCBWidget()
    test_block = OCBCodeBlock(title="Testing block", source=SOURCE_TEST)
    ocb_widget.scene.addItem(test_block)
    wnd.mdiArea.addSubWindow(ocb_widget)

    # Let's run the block !
    pyeditor = test_block.source_editor.widget()
    # pyeditor.setModified(True)
    # test_block._source = ""
    QApplication.processEvents()
    QtTest.QTest.mouseClick(pyeditor,Qt.MouseButton.LeftButton)
    QApplication.processEvents()
    QtTest.QTest.keyPress(pyeditor," ")
    QApplication.processEvents()
    
    # Click outside the block to lose focus of the previous block.
    # This will need to be changed by the click to the run button.
    QtTest.QTest.mouseClick(ocb_widget,Qt.MouseButton.LeftButton)
    QApplication.processEvents()

    # When the execution becomes non-blocking for the UI, a refactor will be needed here.
    result = test_block.stdout.strip()
    
    check.equal(expected_result,result)
    wnd.close()
"""
