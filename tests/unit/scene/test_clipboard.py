# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Unit tests for the pyflow history module. """

import pytest
from pytest_mock import MockerFixture
import pytest_check as check

from pyflow.scene.clipboard import SceneClipboard


class TestSerializeSelected:

    """SceneClipboard._serializeSelected"""

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        self.scene = mocker.MagicMock()
        self.view = mocker.MagicMock()

        self.scene.views.return_value = [self.view]

        self.blocks = [mocker.MagicMock(), mocker.MagicMock()]
        for i, block in enumerate(self.blocks):
            block.serialize.return_value = f"block_{i}"

            dummy_sockets_in = [mocker.MagicMock()]
            dummy_sockets_in[0].id = i
            block.sockets_in = dummy_sockets_in

            dummy_sockets_out = [mocker.MagicMock()]
            dummy_sockets_out[0].id = len(self.blocks) + i
            block.sockets_out = dummy_sockets_out

        self.edges = [mocker.MagicMock(), mocker.MagicMock()]
        dummy_edges_links = [(0, len(self.blocks)), (len(self.blocks), 1)]
        for i, edge in enumerate(self.edges):
            edge.serialize.return_value = f"edge_{i}"

            edge.source_socket.id = dummy_edges_links[i][0]
            edge.destination_socket.id = dummy_edges_links[i][1]

        self.scene.sortedSelectedItems.return_value = self.blocks, self.edges
        self.clipboard = SceneClipboard(self.scene)

    def test_serialize_selected_blocks(self, mocker: MockerFixture):
        """should allow for blocks serialization."""
        data = self.clipboard._serializeSelected()
        check.equal(data["blocks"], [block.serialize() for block in self.blocks])

    def test_serialize_selected_edges(self, mocker: MockerFixture):
        """should allow for edges serialization."""
        data = self.clipboard._serializeSelected()
        check.equal(data["edges"], [edge.serialize() for edge in self.edges])

    def test_serialize_partially_selected_edges(self, mocker: MockerFixture):
        """should not allow for partially selected edges serialization."""
        self.scene.sortedSelectedItems.return_value = self.blocks[0], self.edges
        data = self.clipboard._serializeSelected()
        check.equal(data["edges"], [self.edges[0].serialize()])

    def test_serialize_delete(self, mocker: MockerFixture):
        """should allow for items deletion after serialization."""
        self.clipboard._serializeSelected(delete=True)
        check.is_true(self.view.deleteSelected.called)
