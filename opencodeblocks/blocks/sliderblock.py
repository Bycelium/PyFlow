# OpenCodeBlock an open-source tool for modular visual programing in python

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSlider
from opencodeblocks.blocks.block import OCBBlock

class OCBSliderBlock(OCBBlock):
    """
    Features a slider ranging from 0 to 1 and an area to choose what value to assign the slider to.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.slider = QSlider(Qt.Horizontal)

        self.splitter.addWidget(self.slider)
        
        self.holder.setWidget(self.root)
        
    def update_all(self):
        """ Update the slider. """
        super().update_all()
        if hasattr(self, 'slider'):
            self.slider.setGeometry(
                int(2 * self.edge_size),
                int(self.title_widget.height() + 2 * self.edge_size),
                int(self.width - 8 * self.edge_size),
                int(2 * self.edge_size)
            )