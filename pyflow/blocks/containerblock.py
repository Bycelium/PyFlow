"""
Exports ContainerBlock.
"""

from PyQt5.QtWidgets import QVBoxLayout
from pyflow.blocks.block import Block


class ContainerBlock(Block):
    """
    A block that can contain other blocks.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Defer import to prevent circular dependency.
        # Due to the overall structure of the code, this cannot be removed, as the
        # scene should be able to serialize blocks.
        # This is not due to bad code design and should not be removed.
        from pyflow.graphics.view import (
            View,
        )  # pylint: disable=cyclic-import
        from pyflow.scene.scene import Scene  # pylint: disable=cyclic-import

        self.layout = QVBoxLayout(self.root)
        self.layout.setContentsMargins(
            self.edge_size * 2,
            self.title_widget.height() + self.edge_size * 2,
            self.edge_size * 2,
            self.edge_size * 2,
        )

        self.child_scene = Scene()
        self.child_view = View(self.child_scene)
        self.layout.addWidget(self.child_view)

        self.holder.setWidget(self.root)
