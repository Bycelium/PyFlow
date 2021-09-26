# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

from opencodeblocks.core.node import Node
from opencodeblocks.graphics.block import OCBBlock
import os, sys
from qtpy.QtWidgets import QApplication

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))

from opencodeblocks.graphics.window import OCBWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    wnd = OCBWindow()

    test_block = OCBBlock(Node("Test Block"))
    wnd.scene.addItem(test_block)

    wnd.show()

    sys.exit(app.exec_())
