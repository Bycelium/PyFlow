""" Module for converting ipyg data to ipynb data """

from typing import OrderedDict, List

import copy

from opencodeblocks.scene.ipynb_conversion_constants import *


def ipyg_to_ipynb(data: OrderedDict) -> OrderedDict:
    """Convert ipyg data (as ordered dict) into ipynb data (as ordered dict)"""
    ordered_data: OrderedDict = get_block_in_order(data)

    ipynb_data: OrderedDict = copy.deepcopy(DEFAULT_NOTEBOOK_DATA)

    for block_data in ordered_data["blocks"]:
        if block_data["block_type"] in BLOCK_TYPE_SUPPORTED_FOR_IPYG_TO_IPYNB:
            ipynb_data["cells"].append(block_to_ipynb_cell(block_data))

    return ipynb_data


def get_block_in_order(data: OrderedDict) -> OrderedDict:
    """Changes the order of the blocks from random to the naturel flow of the text"""

    # Not implemented yet
    return data


def block_to_ipynb_cell(block_data: OrderedDict) -> OrderedDict:
    """Convert a ipyg block into its corresponding ipynb cell"""
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
    This is the jupyter notebook default formatting for source, outputs and text"""
    lines = text.split("\n")
    for i in range(len(lines) - 1):
        lines[i] += "\n"
    return lines
