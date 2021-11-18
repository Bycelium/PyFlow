# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import os
import sys

from qtpy.QtWidgets import QApplication
from opencodeblocks.graphics.window import OCBWindow

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    wnd = OCBWindow()
    wnd.show()
    sys.exit(app.exec_())
