# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import os
import sys

from qtpy.QtWidgets import QApplication

from opencodeblocks.graphics.blocks.codeblock import OCBCodeBlock, OCBBlock
from opencodeblocks.graphics.socket import OCBSocket
from opencodeblocks.graphics.window import OCBWindow

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))

SOURCE_TEST = \
'''def build_dataset(a, b):
    """ Build you dataset. """
    return [0, a, 0, b, 1, a]
'''

SOURCE_TEST_2 = \
'''def mon_ia(a, b):
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
    # if hasattr(wnd, 'ocb_widget'):
    #     scene = wnd.ocb_widget.scene

    #     test_block = OCBBlock(title="Other kind of block")
    #     scene.addItem(test_block)
    #     test_block.setPos(-250, 150)

    #     test_block_2 = OCBCodeBlock(title="Dataset", source=SOURCE_TEST)
    #     for _ in range(2):
    #         test_block_2.add_socket(OCBSocket(test_block_2, socket_type='input'))
    #     for _ in range(1):
    #         test_block_2.add_socket(OCBSocket(test_block_2, socket_type='output'))
    #     test_block_2.setPos(-350, -100)
    #     scene.addItem(test_block_2)

    #     test_block_3 = OCBCodeBlock(title="Mon IA (par blocks ?)", source=SOURCE_TEST_2)
    #     for _ in range(2):
    #         test_block_3.add_socket(OCBSocket(test_block_3, socket_type='input'))
    #     for _ in range(1):
    #         test_block_3.add_socket(OCBSocket(test_block_3, socket_type='output'))
    #     test_block_3.setPos(0, -100)
    #     scene.addItem(test_block_3)

    #     # for i in range(3):
    #     #     edge = OCBEdge(
    #     #         source_socket=test_block_3.sockets_out[0],
    #     #         destination_socket=test_block_2.sockets_in[i]
    #     #     )
    #     #     scene.addItem(edge)

    wnd.show()
    sys.exit(app.exec_())
