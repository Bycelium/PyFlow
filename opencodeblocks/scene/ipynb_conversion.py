""" Module for converting ipynb data to ipyg data """

from typing import OrderedDict, List

import json

MARGIN: float = 50

def ipynb_to_ipyg(data: OrderedDict) -> OrderedDict:
    """ Convert ipynb data (ipynb file, as ordered dict) into ipyg data (ipyg, as ordered dict) """

    dataid: int = 0 # TODO : give a proper id

    blocks: List[OrderedDict] = get_blocks(data)

    return {
        "id": dataid,
        "blocks": blocks,
        "edges": []
    }

def get_blocks(data: OrderedDict) -> List[OrderedDict]:
    """ Get the blocks corresponding to a ipynb file, returns them in the ipyg ordered dict format """

    if "cells" not in data:
        return []
    
    blocks: List[OrderedDict] = []

    for cell in data["cells"]:
        if "cell_type" not in cell or cell["cell_type"] != "code":
            pass # TODO : support markdown
        else:
            # Load the default empty block
            # TODO : add something in case the user renames / removes the empty block / changes it too much ?
            data: OrderedDict = {}
            with open("blocks/empty.ocbb", 'r', encoding='utf-8') as file:
                data = json.loads(file.read())

            data["id"] = 0 # TODO : give a proper id

            data["position"] = [
                    len(blocks)*(data["width"] + MARGIN),
                    0
                ]
            
            data["source"] = ''.join(cell["source"])

            data["sockets"] = {} # TODO : add sockets

            # TODO : add support for output

            blocks.append(data)

    return blocks
    