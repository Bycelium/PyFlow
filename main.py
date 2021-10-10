# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import os
import sys

from qtpy.QtWidgets import QApplication

from opencodeblocks.graphics.blocks.codeblock import OCBCodeBlock, OCBBlock
from opencodeblocks.graphics.edge import OCBEdge
from opencodeblocks.graphics.socket import OCBSocket
from opencodeblocks.graphics.window import OCBWindow

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))

SOURCE_TEST = \
'''def absolute_chicken(a, b, chicken=False):
    """ Compute the absolute value of inputs difference. """
    if chicken:
        return 'chicken'
    if a > b:
        return a - b
    else:
        return b - a
'''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    wnd = OCBWindow()
    scene = wnd.ocb_widget.scene

    test_block = OCBBlock(title="Test Block with a very very very long long name")
    for _ in range(3):
        test_block.add_socket(OCBSocket(test_block, socket_type='input'))
    wnd.ocb_widget.scene.addItem(test_block)

    test_block_2 = OCBCodeBlock(title="Test Block 2", source=SOURCE_TEST)
    for _ in range(2):
        test_block_2.add_socket(OCBSocket(test_block_2, socket_type='input'))
    for _ in range(1):
        test_block_2.add_socket(OCBSocket(test_block_2, socket_type='output'))
    test_block_2.setPos(-350, -100)
    scene.addItem(test_block_2)

    for i in range(3):
        edge = OCBEdge(
            source_socket=test_block_2.sockets_out[0],
            destination_socket=test_block.sockets_in[i]
        )
        scene.addItem(edge)

    scene.save('scene.ipyg')
    scene.load('scene.ipyg')

    wnd.show()
    sys.exit(app.exec_())
