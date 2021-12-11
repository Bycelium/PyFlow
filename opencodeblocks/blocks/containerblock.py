"""
Exports OCBContainerBlock.
"""

from opencodeblocks.blocks.block import OCBBlock


class OCBContainerBlock(OCBBlock):
    """
        A block that can contain other blocks.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # WIP