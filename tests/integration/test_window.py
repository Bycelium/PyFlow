# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Integration tests for the OCBWindow.
"""

import os
import pytest

from pytest_mock import MockerFixture
from opencodeblocks.graphics.window import OCBWindow


class TestWindow:
    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        """Setup reused variables."""
        self.window = OCBWindow()

    def test_window_close(self, qtbot):
        """closes"""
        self.window.close()

    def test_open_file(self):
        """loads files"""
        wnd = OCBWindow()
        file_example_path = "./tests/assets/example_graph1.ipyg"
        subwnd = wnd.createNewMdiChild(os.path.abspath(file_example_path))
        subwnd.show()
        wnd.close()
