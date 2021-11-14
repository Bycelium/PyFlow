"""
Integration tests for OCB.

Every test describes a thing the user might try to do.

Important note:
Due to a bug in pytest, if an error occurs in a test, pytest might crash and report an error
that looks like this:

    Windows fatal exception: access violation

    Thread 0x000002a4 (most recent call first):
    <Stack Trace involving native python libraries related to asyncio>

This behavior is not consistent because the crash depends on the memory layout of the program.
If this occurs, you can check what the real error is (with the proper error message), by running
this file directly with:

python ./tests/integration/test_blocks.py

"""
import time, threading, queue, os, sys
import pytest
from pytest_mock import MockerFixture
import pytest_check as check

if __name__ == "__main__":
    # Only works when cwd == <stuff>/OpenCodeBlocks
    sys.path.insert(0, os.path.abspath("."))
 
if sys.platform == "linux":
    os.environ['DISPLAY'] = ":0"

from qtpy.QtWidgets import QApplication
from opencodeblocks.graphics.blocks.codeblock import OCBCodeBlock
from opencodeblocks.graphics.socket import OCBSocket
from opencodeblocks.graphics.window import OCBWindow
from opencodeblocks.graphics.widget import OCBWidget

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QFocusEvent, QMouseEvent
from PyQt5.QtCore import QCoreApplication, QEvent, Qt, QPointF, QPoint
from PyQt5 import QtTest

# Used to move mouse and other high level actions
# We need to use this instead of QTest because of a Qt5 bug (fixed in Qt6) that prevents
# us from simulating mouse dragging
import pyautogui

# The window and app variable used by every test.
wnd = None
app = None


@pytest.fixture
def clean_up():
    global wnd,app

    if wnd != None:
        wnd.close()
        wnd = None
    if app != None:
        app.quit()
        app = None

@pytest.mark.usefixtures('clean_up')
def test_window_opening():
    """ The OCBWindow should open and close correctly """
    global wnd,app

    from qtpy.QtWidgets import QApplication
    from opencodeblocks.graphics.blocks.codeblock import OCBCodeBlock, OCBBlock
    from opencodeblocks.graphics.socket import OCBSocket
    from opencodeblocks.graphics.window import OCBWindow

    app = QApplication([])
    app.setStyle('Fusion')
    wnd = OCBWindow()

@pytest.mark.usefixtures('clean_up')
def test_running_python():
    """ The blocks should run arbitrary python when unfocused """
    global app,wnd

    app = QApplication([])
    app.setStyle('Fusion')
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

@pytest.mark.usefixtures('clean_up')
def test_move_blocks():
    """ 
    Newly created blocks are displayed in the center.
    They can be dragged around with the mouse.
    """
    global app,wnd

    app = QApplication([])
    app.setStyle('Fusion')
    wnd = OCBWindow()
    
    ocb_widget = OCBWidget()
    wnd.mdiArea.addSubWindow(ocb_widget)

    test_block1 = OCBCodeBlock(title="Testing block 1", source="print(1)")
    ocb_widget.scene.addItem(test_block1)

    test_block2 = OCBCodeBlock(title="Testing block 2", source="print(2)")
    ocb_widget.scene.addItem(test_block2)

    QApplication.processEvents()

    expected_move_amount = [70,-30]
    STOP_MSG = "stop"
    CHECK_MSG = "check"

    msgQueue = queue.Queue()

    def testing_drag(msgQueue):
        time.sleep(.4) # Wait for proper setup of app
        
        # test_block1 == (0,0) but it's not crucial for this test.
        pos_block_1 = QPoint(int(test_block1.pos().x()),int(test_block1.pos().y()))
        
        pos_block_1.setX(pos_block_1.x() + 
            test_block1.title_height//2 + 
            ocb_widget.width()//2)
        pos_block_1.setY(pos_block_1.y() + 
            #test_block1.title_height//2 + 
            ocb_widget.height()//2)

        pos_block_1 = ocb_widget.mapToGlobal(pos_block_1)
        
        pyautogui.moveTo(pos_block_1.x(),pos_block_1.y())
        pyautogui.mouseDown(button="left")

        iterations = 5
        for i in range(iterations+1):
            time.sleep(0.05)
            pyautogui.moveTo(
                pos_block_1.x() + expected_move_amount[0] * i // iterations,
                pos_block_1.y() + expected_move_amount[1] * i // iterations
            )
    
        pyautogui.mouseUp(button="left")
        time.sleep(.2)

        move_amount = [test_block2.pos().x(),test_block2.pos().y()]
        # rectify because the scene can be zoomed :
        move_amount[0] = int(move_amount[0] * ocb_widget.view.zoom)
        move_amount[1] = int(move_amount[1] * ocb_widget.view.zoom)

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
        time.sleep(0.02)
        if not msgQueue.empty():
            msg = msgQueue.get()
            if msg[0] == STOP_MSG:
                break
            elif msg[0] == CHECK_MSG:
                check.equal(msg[1],msg[2],msg[3])
    t.join()

if __name__ == "__main__":
    test_running_python()