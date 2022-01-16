# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for converting notebook (.ipynb) data to pygraph (.ipyg) data."""

from typing import OrderedDict, List

from PyQt5.QtGui import QFontMetrics, QFont

from pyflow.scene.ipynb_conversion_constants import *
from pyflow.graphics.theme_manager import theme_manager
from pyflow.blocks.pyeditor import POINT_SIZE


def ipynb_to_ipyg(data: OrderedDict, use_theme_font: bool = True) -> OrderedDict:
    """
    Convert ipynb data (ipynb file, as ordered dict) into ipyg data (ipyg, as ordered dict)
    - use_theme_font: should the height of the blocks be computed based on the current
    font selected.
    """

    blocks_data: List[OrderedDict] = get_blocks_data(data, use_theme_font)
    edges_data: List[OrderedDict] = get_edges_data(blocks_data)

    return {
        "blocks": blocks_data,
        "edges": edges_data,
    }


def get_blocks_data(
    data: OrderedDict, use_theme_font: bool = True
) -> List[OrderedDict]:
    """
    Get the blocks corresponding to a ipynb file,
    Returns them in the ipyg ordered dict format
    """

    if "cells" not in data:
        return []

    # Get the font metrics to determine the size fo the blocks
    fontmetrics = None
    if use_theme_font:
        font = QFont()
        font.setFamily(theme_manager().recommended_font_family)
        font.setFixedPitch(True)
        font.setPointSize(POINT_SIZE)
        fontmetrics = QFontMetrics(font)

    blocks_data: List[OrderedDict] = []

    next_block_x_pos: float = 0
    next_block_y_pos: float = 0
    next_block_id = 0

    for cell in data["cells"]:
        if "cell_type" not in cell or cell["cell_type"] not in ["code", "markdown"]:
            pass
        else:
            block_type: str = cell["cell_type"]

            text: List[str] = []

            if isinstance(cell["source"], list):
                text: str = cell["source"]
            elif isinstance(cell["source"], str):
                text = [line + "\n" for line in cell["source"].split("\n")]
            else:
                raise TypeError("A cell's source is not of the right type")

            text_width = DEFAULT_TEXT_WIDTH
            if use_theme_font:
                text_width: float = (
                    max(fontmetrics.boundingRect(line).width() for line in text)
                    if len(text) > 0
                    else 0
                )
            block_width: float = min(
                max(text_width + MARGIN_X, BLOCK_MIN_WIDTH), BLOCK_MAX_WIDTH
            )

            lineSpacing = DEFAULT_LINE_SPACING
            lineHeight = DEFAULT_LINE_HEIGHT

            if use_theme_font:
                lineSpacing = fontmetrics.lineSpacing()
                lineHeight = fontmetrics.lineWidth()

            text_height: float = len(text) * (lineSpacing + lineHeight)
            block_height: float = text_height + MARGIN_Y

            block_data = {
                "id": next_block_id,
                "block_type": BLOCK_TYPE_TO_NAME[block_type],
                "width": block_width,
                "height": block_height,
                "position": [
                    next_block_x_pos,
                    next_block_y_pos,
                ],
                "sockets": [],
            }

            if block_type == "code":
                block_data["source"] = "".join(text)
                next_block_y_pos = 0
                next_block_x_pos += block_width + MARGIN_BETWEEN_BLOCKS_X

                if len(blocks_data) > 0 and is_title(blocks_data[-1]):
                    block_title: OrderedDict = blocks_data.pop()
                    block_data["title"] = block_title["text"]

                    # Revert position effect of the markdown block
                    block_data["position"] = block_title["position"]
            elif block_type == "markdown":
                block_data.update(
                    {
                        "text": "".join(text),
                    }
                )
                next_block_y_pos += block_height + MARGIN_BETWEEN_BLOCKS_Y

            blocks_data.append(block_data)
            next_block_id += 1

    adujst_markdown_blocks_width(blocks_data)

    return blocks_data


def is_title(block_data: OrderedDict) -> bool:
    """Checks if the block is a one-line markdown block which could correspond to a title."""
    if block_data["block_type"] != BLOCK_TYPE_TO_NAME["markdown"]:
        return False
    if "\n" in block_data["text"]:
        return False
    if not block_data["text"] or len(block_data["text"]) > TITLE_MAX_LENGTH:
        return False
    # Headings, quotes, bold or italic text are not considered to be headings
    if block_data["text"][0] in {"#", "*", "`"}:
        return False
    return True


def adujst_markdown_blocks_width(blocks_data: OrderedDict) -> None:
    """
    Modify the markdown blocks width (in place)
    For them to match the width of block of code below
    """
    i: int = len(blocks_data) - 1

    while i >= 0:
        if blocks_data[i]["block_type"] == BLOCK_TYPE_TO_NAME["code"]:
            block_width: float = blocks_data[i]["width"]
            i -= 1

            while (
                i >= 0
                and blocks_data[i]["block_type"] == BLOCK_TYPE_TO_NAME["markdown"]
            ):
                blocks_data[i]["width"] = block_width
                i -= 1
        else:
            i -= 1


def get_edges_data(blocks_data: OrderedDict) -> OrderedDict:
    """Add sockets to the blocks (in place) and returns the edge list."""
    code_blocks: List[OrderedDict] = [
        block
        for block in blocks_data
        if block["block_type"] == BLOCK_TYPE_TO_NAME["code"]
    ]
    edges_data: List[OrderedDict] = []

    greatest_block_id: int = 0
    if len(blocks_data) > 0:
        greatest_block_id = blocks_data[-1]["id"]

    last_socket_id_out: int = -1
    for i, block in enumerate(code_blocks):
        socket_id_out: int = greatest_block_id + 2 * i + 2
        socket_id_in: int = greatest_block_id + 2 * i + 1

        block["sockets"].append(get_output_socket_data(socket_id_out, block["width"]))
        block["sockets"].append(get_input_socket_data(socket_id_in))

        if i >= 1:
            edges_data.append(
                get_edge_data(
                    i,
                    code_blocks[i - 1]["id"],
                    last_socket_id_out,
                    code_blocks[i]["id"],
                    socket_id_in,
                )
            )

        last_socket_id_out = socket_id_out

    return edges_data


def get_input_socket_data(socket_id: int) -> OrderedDict:
    """Returns the input socket's data with the corresponding id."""
    return {
        "id": socket_id,
        "type": "input",
        "position": [0.0, SOCKET_HEIGHT],
    }


def get_output_socket_data(socket_id: int, block_width: int) -> OrderedDict:
    """
    Returns the input socket's data with the corresponding id
    and at the correct relative position with respect to the block
    """
    return {
        "id": socket_id,
        "type": "output",
        "position": [block_width, SOCKET_HEIGHT],
    }


def get_edge_data(
    edge_id: int,
    edge_start_block_id: int,
    edge_start_socket_id: int,
    edge_end_block_id: int,
    edge_end_socket_id: int,
) -> OrderedDict:
    """Return the ordered dict corresponding to the given parameters."""
    return {
        "id": edge_id,
        "source": {"block": edge_start_block_id, "socket": edge_start_socket_id},
        "destination": {"block": edge_end_block_id, "socket": edge_end_socket_id},
    }
