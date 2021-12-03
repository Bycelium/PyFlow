""" Module for converting ipynb data to ipyg data """

from pickle import DICT
from typing import OrderedDict, List

import json

MARGIN_X: float = 50
MARGIN_Y: float = 50
TEXT_SIZE: float = 12
TEXT_SIZE_TO_WIDTH_RATIO: float = 0.7
TEXT_SIZE_TO_HEIGHT_RATIO: float = 1.42
ipyg_id_generator = lambda: 0
block_id_generator = lambda: 0

BLOCK_TYPE_TO_NAME: DICT= {
    "code" : "OCBCodeBlock",
    "markdown" : "OCBMarkdownBlock"
}

def ipynb_to_ipyg(data: OrderedDict) -> OrderedDict:
    """ Convert ipynb data (ipynb file, as ordered dict) into ipyg data (ipyg, as ordered dict) """

    blocks: List[OrderedDict] = get_blocks(data)

    return {
        "id": ipyg_id_generator(),
        "blocks": blocks,
        "edges": []
    }

def get_blocks(data: OrderedDict) -> List[OrderedDict]:
    """ Get the blocks corresponding to a ipynb file, returns them in the ipyg ordered dict format """

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

            text_width: float = TEXT_SIZE * TEXT_SIZE_TO_WIDTH_RATIO * max(len(line) for line in text)
            block_width: float = text_width + MARGIN_X
            text_height: float = TEXT_SIZE * TEXT_SIZE_TO_HEIGHT_RATIO * len(text)
            block_height: float = text_height + MARGIN_Y
            
            block = {
                "id": block_id_generator(),
                "title": "_",
                "block_type": BLOCK_TYPE_TO_NAME[block_type],
                "width": block_width,
                "height": block_height,
                "position": [
                    next_block_x_pos,
                    next_block_y_pos
                ],
                "splitter_pos": [
                    85,
                    261
                ],
                "sockets": [],
                "metadata": {
                    "title_metadata": {
                        "color": "white",
                        "font": "Ubuntu",
                        "size": 12,
                        "padding": 4.0
                    }
                }
            }

            if block_type == "code":
                block.update({
                    "source": ''.join(text),
                    "stdout": ''
                })
                next_block_y_pos = 0
                next_block_x_pos += block_width
            elif block_type == "markdown":
                block.update({
                    "text": ''.join(text)
                })
                next_block_y_pos += block_height


            blocks.append(block)


    return blocks
    