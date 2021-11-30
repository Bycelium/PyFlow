# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Unit tests for the opencodeblocks history module. """

import pytest
from pytest_mock import MockerFixture
import pytest_check as check

from opencodeblocks.scene.history import SceneHistory


class TestUndo:

    """Undo"""

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        self.scene = mocker.MagicMock()
        self.history = SceneHistory(self.scene, max_stack=6)
        self.history.history_stack = ["A", "B", "C", "D"]
        self.history.current = 3

    def test_undo(self, mocker: MockerFixture):
        """should allow for undo without breaking the history stack."""
        mocker.patch("opencodeblocks.scene.history.SceneHistory.restore")

        check.equal(self.history.history_stack, ["A", "B", "C", "D"])
        check.equal(self.history.history_stack[self.history.current], "D")

        self.history.undo()

        check.equal(self.history.history_stack, ["A", "B", "C", "D"])
        check.equal(self.history.history_stack[self.history.current], "C")
        check.is_true(self.history.restore.called)

    def test_undo_nostack(self, mocker: MockerFixture):
        """should allow to undo without any change if the history stack is empty."""
        mocker.patch("opencodeblocks.scene.history.SceneHistory.restore")

        self.history.history_stack = []
        self.history.current = -1

        self.history.undo()

        check.equal(self.history.history_stack, [])
        check.equal(self.history.current, -1)
        check.is_false(self.history.restore.called)

    def test_undo_end_of_stack(self, mocker: MockerFixture):
        """should allow to undo without any change if at the end of the history stack."""
        mocker.patch("opencodeblocks.scene.history.SceneHistory.restore")

        self.history.current = 0
        check.equal(self.history.history_stack, ["A", "B", "C", "D"])
        check.equal(self.history.history_stack[self.history.current], "A")

        self.history.undo()

        check.equal(self.history.history_stack, ["A", "B", "C", "D"])
        check.equal(self.history.history_stack[self.history.current], "A")
        check.is_false(self.history.restore.called)


class TestRedo:

    """Redo"""

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        self.scene = mocker.MagicMock()
        self.history = SceneHistory(self.scene, max_stack=6)
        self.history.history_stack = ["A", "B", "C", "D"]
        self.history.current = 1

    def test_redo(self, mocker: MockerFixture):
        """should allow for redo without changing the history stack."""
        mocker.patch("opencodeblocks.scene.history.SceneHistory.restore")

        check.equal(self.history.history_stack, ["A", "B", "C", "D"])
        check.equal(self.history.history_stack[self.history.current], "B")

        self.history.redo()

        check.equal(self.history.history_stack, ["A", "B", "C", "D"])
        check.equal(self.history.history_stack[self.history.current], "C")
        check.is_true(self.history.restore.called)

    def test_redo_nostack(self, mocker: MockerFixture):
        """should allow to redo without any change if the history stack is empty."""
        mocker.patch("opencodeblocks.scene.history.SceneHistory.restore")

        self.history.history_stack = []
        self.history.current = -1

        self.history.redo()

        check.equal(self.history.history_stack, [])
        check.equal(self.history.current, -1)
        check.is_false(self.history.restore.called)

    def test_redo_end_of_stack(self, mocker: MockerFixture):
        """should allow to redo without any change if at the beggining of the history stack."""
        mocker.patch("opencodeblocks.scene.history.SceneHistory.restore")

        self.history.current = 3
        check.equal(self.history.history_stack, ["A", "B", "C", "D"])
        check.equal(self.history.history_stack[self.history.current], "D")

        self.history.redo()

        check.equal(self.history.history_stack, ["A", "B", "C", "D"])
        check.equal(self.history.history_stack[self.history.current], "D")
        check.is_false(self.history.restore.called)


class TestStore:

    """Store"""

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        self.scene = mocker.MagicMock()
        self.history = SceneHistory(self.scene, max_stack=6)

    def test_store(self):
        """should update current while storing new data."""
        self.history.history_stack = ["A", "B", "C", "D"]
        self.history.current = 3

        self.history.store("E")

        check.equal(self.history.history_stack, ["A", "B", "C", "D", "E"])
        check.equal(self.history.history_stack[self.history.current], "E")

    def test_store_cut(self):
        """should cut upper stack when storing new data."""
        self.history.history_stack = ["A", "B", "C", "D"]
        self.history.current = 2

        self.history.store("E")

        check.equal(self.history.history_stack, ["A", "B", "C", "E"])
        check.equal(self.history.history_stack[self.history.current], "E")

    def test_store_max_stack(self):
        """should forget oldests checkpoint when storing new data at maximum stack size."""
        self.history.history_stack = ["A", "B", "C", "D"]
        self.history.current = 3
        self.history.max_stack = 4

        self.history.store("E")

        check.equal(self.history.history_stack, ["B", "C", "D", "E"])
        check.equal(self.history.history_stack[self.history.current], "E")
