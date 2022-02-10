# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the ContainerBlock.

A block that can contain other blocks.

"""

from PyQt5.QtWidgets import QVBoxLayout
from pyflow.blocks.block import Block


class ContainerBlock(Block):
    """
    A block that can contain other blocks.
    """

    def __init__(self, **kwargs):
        super().__init__(block_type="ContainerBlock", **kwargs)

        # Defer import to prevent circular dependency.
        # Due to the overall structure of the code, this cannot be removed, as the
        # scene should be able to serialize blocks.
        # This is not due to bad code design and should not be removed.
        # pylint: disable=import-outside-toplevel, cyclic-import
        from pyflow.graphics.view import View
        from pyflow.scene.scene import Scene

        self.layout = QVBoxLayout(self.root)
        self.layout.setContentsMargins(
            int(self.edge_size * 2),
            int(self.title_widget.height() + self.edge_size * 2),
            int(self.edge_size * 2),
            int(self.edge_size * 2),
        )

        self.child_scene = Scene()
        self.child_view = View(self.child_scene)
        self.layout.addWidget(self.child_view)

        self.holder.setWidget(self.root)
