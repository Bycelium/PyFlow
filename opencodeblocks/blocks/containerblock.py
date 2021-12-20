"""
Exports OCBContainerBlock.
"""

from PyQt5.QtWidgets import QVBoxLayout
from opencodeblocks.blocks.block import OCBBlock


class OCBContainerBlock(OCBBlock):
    """
    A block that can contain other blocks.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Defer import to prevent circular dependency.
        # Due to the overall structure of the code, this cannot be removed, as the
        # scene should be able to serialize blocks.
        # This is not due to bad code design and should not be removed.
        from opencodeblocks.graphics.view import (
            OCBView,
        )  # pylint: disable=cyclic-import
        from opencodeblocks.scene.scene import OCBScene  # pylint: disable=cyclic-import

        self.layout = QVBoxLayout(self.root)
        self.layout.setContentsMargins(
            self.edge_size * 2,
            self.title_widget.height() + self.edge_size * 2,
            self.edge_size * 2,
            self.edge_size * 2,
        )

        self.child_scene = OCBScene()
        self.child_view = OCBView(self.child_scene)
        self.layout.addWidget(self.child_view)

        self.holder.setWidget(self.root)
