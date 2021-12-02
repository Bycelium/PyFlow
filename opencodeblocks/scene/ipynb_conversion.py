""" Module for converting ipynb data to ipyg data """

from typing import OrderedDict, List

def ipynb_to_ipyg(data: OrderedDict) -> OrderedDict:
    id: int = 0

    blocks: List[OrderedDict] = get_blocks(data)

    return {
        "id": id,
        "blocks": blocks,
        "edges": []
    }

def get_blocks(data: OrderedDict) -> List[OrderedDict]:
    if "cells" not in data:
        return []
    
    blocks: List[OrderedDict] = []

    # Markdown cells to be passed to the next code block
    markdown_blocks: List[OrderedDict] = []
    for cell in data["cells"]:
        if "cell_type" not in cell or cell["cell_type"] != "code":
            pass # Not supported yet
        else:
            blocks.append({
                "id": 0,
                "title": "_",
                "block_type": "code",
                "source": ''.join(cell["source"]),
                "stdout": '',
                "width": 500,
                "height": 200,
                "position": [
                    len(blocks)*500,
                    0
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
            })

    return blocks