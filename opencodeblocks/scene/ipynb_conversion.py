""" Module for converting ipynb data to ipyg data """

from typing import OrderedDict, List, Dict

MARGIN_X: float = 50
MARGIN_Y: float = 50
BLOCK_MIN_WIDTH = 400
TEXT_SIZE: float = 12
TEXT_SIZE_TO_WIDTH_RATIO: float = 0.7
TEXT_SIZE_TO_HEIGHT_RATIO: float = 1.42
ipyg_id_generator = lambda: 0
block_id_generator = lambda: 0

BLOCK_TYPE_TO_NAME: Dict[str, str] = {
    "code": "OCBCodeBlock",
    "markdown": "OCBMarkdownBlock",
}


def ipynb_to_ipyg(data: OrderedDict) -> OrderedDict:
    """Convert ipynb data (ipynb file, as ordered dict) into ipyg data (ipyg, as ordered dict)"""

    blocks: List[OrderedDict] = get_blocks(data)

    return {
        "id": ipyg_id_generator(),
        "blocks": blocks,
        "edges": [],
    }


def get_blocks(data: OrderedDict) -> List[OrderedDict]:
    """
    Get the blocks corresponding to a ipynb file,
    Returns them in the ipyg ordered dict format
    """

    if "cells" not in data:
        return []

    blocks: List[OrderedDict] = []

    next_block_x_pos: float = 0
    next_block_y_pos: float = 0

    for cell in data["cells"]:
        if "cell_type" not in cell or cell["cell_type"] not in ["code", "markdown"]:
            pass
        else:
            block_type = cell["cell_type"]

            text = cell["source"]

            text_width: float = (
                TEXT_SIZE * TEXT_SIZE_TO_WIDTH_RATIO * max(len(line) for line in text)
                if len(text) > 0
                else 0
            )
            block_width: float = max(text_width + MARGIN_X, BLOCK_MIN_WIDTH)
            text_height: float = TEXT_SIZE * TEXT_SIZE_TO_HEIGHT_RATIO * len(text)
            block_height: float = text_height + MARGIN_Y

            block = get_default_block()

            block.update(
                {
                    "block_type": BLOCK_TYPE_TO_NAME[block_type],
                    "width": block_width,
                    "height": block_height,
                    "position": [
                        next_block_x_pos,
                        next_block_y_pos,
                    ],
                }
            )

            if block_type == "code":
                block.update(
                    {
                        "source": "".join(text),
                        "stdout": "",
                    }
                )
                next_block_y_pos = 0
                next_block_x_pos += block_width
            elif block_type == "markdown":
                block.update(
                    {
                        "text": "".join(text),
                    }
                )
                next_block_y_pos += block_height

            blocks.append(block)

    adujst_markdown_blocks_width(blocks)

    return blocks


def get_default_block() -> OrderedDict:
    """Return a default block with argument that vary missing"""
    return {
        "id": block_id_generator(),
        "title": "_",
        "splitter_pos": [
            85,
            261,
        ],
        "sockets": [],
        "metadata": {
            "title_metadata": {
                "color": "white",
                "font": "Ubuntu",
                "size": 12,
                "padding": 4.0,
            }
        },
    }


def adujst_markdown_blocks_width(blocks: OrderedDict) -> None:
    """Modify the markdown blocks width for them to match the width of block of code below"""
    i: int = len(blocks) - 1

    while i >= 0:
        if blocks[i]["block_type"] == BLOCK_TYPE_TO_NAME["code"]:
            block_width = blocks[i]["width"]
            i -= 1

            while i >= 0 and blocks[i]["block_type"] == BLOCK_TYPE_TO_NAME["markdown"]:
                blocks[i]["width"] = block_width
                i -= 1
        else:
            i -= 1
