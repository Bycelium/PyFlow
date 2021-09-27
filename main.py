# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import os, sys

from qtpy.QtWidgets import QApplication

from opencodeblocks.core.node import CodeNode
from opencodeblocks.graphics.block import OCBBlock
from opencodeblocks.graphics.window import OCBWindow

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    wnd = OCBWindow()

    test_block = OCBBlock(CodeNode(title="Test Block with a very very very long long name"))
    test_block.add_socket()
    test_block.add_socket()
    test_block.add_socket()
    test_block.add_socket()
    test_block.add_socket()
    test_block.add_socket('output')
    test_block.add_socket('output')
    test_block.add_socket('output')
    wnd.scene.addItem(test_block)

    wnd.show()

    sys.exit(app.exec_())
