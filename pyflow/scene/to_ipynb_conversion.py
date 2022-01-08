# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for converting pygraph (.ipyg) data to notebook (.ipynb) data."""

from typing import OrderedDict, List

import copy

from pyflow.scene.ipynb_conversion_constants import *


def ipyg_to_ipynb(data: OrderedDict) -> OrderedDict:
    """Convert ipyg data (as ordered dict) into ipynb data (as ordered dict)."""
    ordered_blocks: OrderedDict = get_block_in_order(data)

    ipynb_data: OrderedDict = copy.deepcopy(DEFAULT_NOTEBOOK_DATA)

    for block_data in ordered_blocks:
        if block_data["block_type"] in BLOCK_TYPE_SUPPORTED_FOR_IPYG_TO_IPYNB:
            ipynb_data["cells"].append(block_to_ipynb_cell(block_data))

    return ipynb_data


def get_block_in_order(data: OrderedDict) -> OrderedDict:
    """Change the order of the blocks from random to the naturel flow of the documents.

    Markdown blocks are put in a random order at the end of the document.
    Other blocks are not saved."""

    blocks_data = data["blocks"]
    edges_data = data["edges"]

    code_blocks: List[OrderedDict] = [
        block
        for block in blocks_data
        if block["block_type"] == BLOCK_TYPE_TO_NAME["code"]
    ]
    markdown_blocks: List[OrderedDict] = [
        block
        for block in blocks_data
        if block["block_type"] == BLOCK_TYPE_TO_NAME["markdown"]
    ]

    # The adjacency map
    adjacency_map: Dict[int, List[int]] = {}
    # Initialize the map
    for block in code_blocks:
        adjacency_map[block["id"]] = []
    # Fill the map with the data contained in the edges
    for edge in edges_data:
        # Add edges linking two coding blocks together
        if (
            edge["source"]["block"] in adjacency_map
            and edge["destination"]["block"] in adjacency_map
        ):
            adjacency_map[edge["source"]["block"]].append(edge["destination"]["block"])

    return topological_sort(code_blocks, adjacency_map) + markdown_blocks


def block_to_ipynb_cell(block_data: OrderedDict) -> OrderedDict:
    """Convert a ipyg block into its corresponding ipynb cell."""
    if block_data["block_type"] == BLOCK_TYPE_TO_NAME["code"]:
        cell_data: OrderedDict = copy.deepcopy(DEFAULT_CODE_CELL)
        cell_data["source"] = split_lines_and_add_newline(block_data["source"])
        return cell_data
    if block_data["block_type"] == BLOCK_TYPE_TO_NAME["markdown"]:
        cell_data: OrderedDict = copy.deepcopy(DEFAULT_MARKDOWN_CELL)
        cell_data["source"] = split_lines_and_add_newline(block_data["text"])
        return cell_data

    raise ValueError(
        f"The block type {block_data['block_type']} is not supported but has been declared as such"
    )


def split_lines_and_add_newline(text: str) -> List[str]:
    """Split the text and add a \\n at the end of each line
    This is the jupyter notebook default formatting for source, outputs and text."""
    lines = text.split("\n")
    for i in range(len(lines) - 1):
        lines[i] += "\n"
    return lines


def topological_sort(
    code_blocks: List[OrderedDict], adjacency_map: Dict[int, List[int]]
) -> List[OrderedDict]:
    """Sort the code blocks according to a (random) topological order.

    The list of blocks sorted is such that block A appears block node B if and only if
    the execution of block A doesn't require the execution of block B.
    It is assumed that the graph doesn't contain any cycle.
    There is no guarantee on the result if it contains one (but a result is provided).

    Args:
        code_blocks: a list of blocks with an "id" field
        adjacency_map: a dictionnary where each key corresponds to the id of a block B,
                        the corresponding value should be the code blocks C where there is
                        an edge going from block B to block C"""

    id_to_block: Dict[int, OrderedDict] = {}
    for block in code_blocks:
        id_to_block[block["id"]] = block

    sorted_blocks: List[OrderedDict] = []

    # The set of the ids of visited blocks
    visited: set[int] = set([])

    def dfs(block_id):
        visited.add(block_id)

        for following_block_id in adjacency_map[block_id]:
            if following_block_id not in visited:
                dfs(following_block_id)

        # Push current block to stack which stores result
        sorted_blocks.append(id_to_block[block_id])

    # Start a dfs on each block one by one
    for block_id in adjacency_map.keys():
        if block_id not in visited:
            dfs(block_id)

    # Reverse the order of the list
    # (The first node added to the list was one with no "child")
    return sorted_blocks[::-1]
