""" Module for converting ipynb data to ipyg data """

from typing import OrderedDict, List

from PyQt5.QtGui import QFontMetrics, QFont

from opencodeblocks.scene.ipynb_conversion_constants import *
from opencodeblocks.graphics.theme_manager import theme_manager
from opencodeblocks.graphics.pyeditor import POINT_SIZE


def ipynb_to_ipyg(data: OrderedDict) -> OrderedDict:
    """Convert ipynb data (ipynb file, as ordered dict) into ipyg data (ipyg, as ordered dict)"""

    blocks_data: List[OrderedDict] = get_blocks_data(data)
    edges_data: List[OrderedDict] = get_edges_data(blocks_data)

    return {
        "blocks": blocks_data,
        "edges": edges_data,
    }


def get_blocks_data(data: OrderedDict) -> List[OrderedDict]:
    """
    Get the blocks corresponding to a ipynb file,
    Returns them in the ipyg ordered dict format
    """

    if "cells" not in data:
        return []

    # Get the font metrics to determine the size fo the blocks
    font = QFont()
    font.setFamily(theme_manager().recommended_font_family)
    font.setFixedPitch(True)
    font.setPointSize(POINT_SIZE)
    fontmetrics = QFontMetrics(font)

    blocks_data: List[OrderedDict] = []

    next_block_x_pos: float = 0
    next_block_y_pos: float = 0

    for cell in data["cells"]:
        if "cell_type" not in cell or cell["cell_type"] not in ["code", "markdown"]:
            pass
        else:
            block_type: str = cell["cell_type"]

            text: str = cell["source"]

            text_width: float = (
                max(fontmetrics.boundingRect(line).width() for line in text)
                if len(text) > 0
                else 0
            )
            block_width: float = max(text_width + MARGIN_X, BLOCK_MIN_WIDTH)
            text_height: float = len(text) * (
                fontmetrics.lineSpacing() + fontmetrics.lineWidth()
            )
            block_height: float = text_height + MARGIN_Y

            block_data = {
                "id": len(blocks_data),
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

    adujst_markdown_blocks_width(blocks_data)

    return blocks_data


def is_title(block_data: OrderedDict) -> bool:
    """Checks if the block is a one-line markdown block which could correspond to a title"""
    if block_data["block_type"] != BLOCK_TYPE_TO_NAME["markdown"]:
        return False
    if "\n" in block_data["text"]:
        return False
    if len(block_data["text"]) == 0 or len(block_data["text"]) > TITLE_MAX_LENGTH:
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
    """Add sockets to the blocks (in place) and returns the edge list"""
    code_blocks: List[OrderedDict] = [
        block
        for block in blocks_data
        if block["block_type"] == BLOCK_TYPE_TO_NAME["code"]
    ]
    edges_data: List[OrderedDict] = []

    for i in range(1, len(code_blocks)):
        socket_id_out = len(blocks_data) + 2 * i
        socket_id_in = len(blocks_data) + 2 * i + 1
        code_blocks[i - 1]["sockets"].append(
            get_output_socket_data(socket_id_out, code_blocks[i - 1]["width"])
        )
        code_blocks[i]["sockets"].append(get_input_socket_data(socket_id_in))
        edges_data.append(
            get_edge_data(
                i,
                code_blocks[i - 1]["id"],
                socket_id_out,
                code_blocks[i]["id"],
                socket_id_in,
            )
        )
    return edges_data


def get_input_socket_data(socket_id: int) -> OrderedDict:
    """Returns the input socket's data with the corresponding id"""
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
    """Return the ordered dict corresponding to the given parameters"""
    return {
        "id": edge_id,
        "source": {"block": edge_start_block_id, "socket": edge_start_socket_id},
        "destination": {"block": edge_end_block_id, "socket": edge_end_socket_id},
    }
