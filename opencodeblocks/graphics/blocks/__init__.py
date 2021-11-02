# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB Blocks of different types. """

from opencodeblocks.graphics.blocks.block import OCBBlock
from opencodeblocks.graphics.blocks.codeblock import OCBCodeBlock

BLOCKS = {
    'base': OCBBlock,
    'code': OCBCodeBlock
}
