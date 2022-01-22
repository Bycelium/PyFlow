# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

"""Unit tests for the conversion from ipynb."""

from typing import List, OrderedDict
from pytest_mock import MockerFixture
import pytest_check as check
import json

from pyflow.scene.from_ipynb_conversion import ipynb_to_ipyg, is_title
from pyflow.scene.ipynb_conversion_constants import BLOCK_TYPE_TO_NAME


class TestFromIpynbConversion:

    """Conversion from .ipynb"""

    def test_empty_data(self, mocker: MockerFixture):
        """should return empty ipyg graph for empty data."""
        check.equal(ipynb_to_ipyg({}, False), {"blocks": [], "edges": []})

    def test_empty_notebook_data(self, mocker: MockerFixture):
        """should return expected graph for a real empty notebook data."""
        file_path = "./tests/assets/empty.ipynb"
        real_notebook_conversion_is_coherent(file_path)

    def test_usual_notebook_data(self, mocker: MockerFixture):
        """should return expected graph for a real usual notebook data."""
        file_path = "./tests/assets/usual.ipynb"
        real_notebook_conversion_is_coherent(file_path)

    def test_complex_notebook_data(self, mocker: MockerFixture):
        """should return expected graph for a real complex notebook data."""
        file_path = "./tests/assets/complex.ipynb"
        real_notebook_conversion_is_coherent(file_path)

    def test_is_title(self, mocker: MockerFixture):
        """should return True iff the given text can be used as a title for a block."""
        check.equal(is_title(string_to_markdown_block("")), False)
        check.equal(is_title(string_to_markdown_block("Data Preprocessing")), True)
        check.equal(is_title(string_to_markdown_block("Étude de cas")), True)
        check.equal(is_title(string_to_markdown_block("# Report")), False)
        check.equal(
            is_title(
                string_to_markdown_block(
                    "This is a very very very very very very very very very very very very very very very very very very long explanation"
                )
            ),
            False,
        )
        check.equal(is_title(string_to_markdown_block("New line \n Next line")), False)


def real_notebook_conversion_is_coherent(file_path: str):
    """Checks that the conversion of the ipynb notebook gives a coherent result.

    Args:
        file_path: the path to a .ipynb file
    """
    ipynb_data = load_json(file_path)
    ipyg_data = ipynb_to_ipyg(ipynb_data, False)
    check_conversion_coherence(ipynb_data, ipyg_data)


def check_conversion_coherence(ipynb_data: OrderedDict, ipyg_data: OrderedDict):
    """Checks that the ipyg data is coherent with the ipynb data.

    The conversion from ipynb to ipyg should return
    1. blocks and edges
    2. the right amount of code blocks and edges
    3. blocks and sockets with unique ids
    4. edges with existing ids
    5. code blocks that always have a source and two sockets
    6. markdown blocks that always have text
    """

    # blocks and edges are present
    check.equal("blocks" in ipyg_data and "edges" in ipyg_data, True)

    # the amount of code blocks and edges is right
    code_blocks_in_ipynb: int = 0
    for cell in ipynb_data["cells"]:
        if cell["cell_type"] == "code":
            code_blocks_in_ipynb += 1
    code_blocks_in_ipyg: int = 0
    for block in ipyg_data["blocks"]:
        if block["block_type"] == BLOCK_TYPE_TO_NAME["code"]:
            code_blocks_in_ipyg += 1
    check.equal(code_blocks_in_ipyg, code_blocks_in_ipynb)

    # blocks and sockets have unique ids
    block_id_set = set([])
    socket_id_set = set([])
    for block in ipyg_data["blocks"]:
        if "id" in block:
            check.equal(block["id"] in block_id_set, False)
            block_id_set.add(block["id"])
        if "sockets" in block:
            for socket in block["sockets"]:
                if "id" in socket:
                    check.equal(socket["id"] in socket_id_set, False)
                    socket_id_set.add(socket["id"])

    # edges are between objects with existing ids
    for edge in ipyg_data["edges"]:
        check.equal(edge["source"]["block"] in block_id_set, True)
        check.equal(edge["destination"]["block"] in block_id_set, True)
        check.equal(edge["source"]["socket"] in socket_id_set, True)
        check.equal(edge["destination"]["socket"] in socket_id_set, True)

    # code blocks always have a source and two sockets
    # markdown blocks always have a text
    for block in ipyg_data["blocks"]:
        if block["block_type"] == BLOCK_TYPE_TO_NAME["code"]:
            check.equal("source" in block, True)
            check.equal(type(block["source"]), str)

            check.equal("sockets" in block, True)
            check.equal(type(block["sockets"]), list)
            check.equal(len(block["sockets"]), 2)

        if block["block_type"] == BLOCK_TYPE_TO_NAME["markdown"]:
            check.equal("text" in block and type(block["text"]) == str, True)


def load_json(file_path: str):
    """Helper function that returns the ipynb data in a given file."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.loads(file.read())
    return data


def string_to_markdown_block(string: str):
    """Helper function that returns the ipyg data necessary for the is_title function to work."""
    return {
        "block_type": BLOCK_TYPE_TO_NAME["markdown"],
        "text": string,
    }
