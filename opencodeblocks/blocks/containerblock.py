"""
Exports OCBContainerBlock.
"""

from PyQt5.QtWidgets import QVBoxLayout
from opencodeblocks.blocks.block import OCBBlock
from opencodeblocks.graphics.view import OCBView
from opencodeblocks.graphics.widget import OCBWidget
from opencodeblocks.scene.scene import OCBScene


class OCBContainerBlock(OCBBlock):
    """
        A block that can contain other blocks.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = QVBoxLayout(self.root)

        self.scene = OCBScene()
        self.scene.addHasBeenModifiedListener(self.updateTitle)
        self.view = OCBView(self.scene)
        self.layout.addWidget(self.view)

        self.holder.setWidget(self.root)
