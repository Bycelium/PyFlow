# OpenCodeBlock an open-source tool for modular visual programing in python

"""
Exports OCBSliderBlock.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QSlider, QVBoxLayout
from opencodeblocks.blocks.block import OCBBlock

class OCBSliderBlock(OCBBlock):
    """
    Features a slider ranging from 0 to 1 and an area to choose what value to assign the slider to.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.layout = QVBoxLayout(self.root)


        self.slider = QSlider(Qt.Horizontal)
        self.slider.valueChanged.connect(self.valueChanged)

        self.variable_layout = QHBoxLayout(self.root)
        self.variable_text = QLineEdit("slider_value")
        self.variable_value = QLabel(f"{self.slider.value()/100}")

        self.variable_text.setFixedWidth(self.root.width() / 2)

        self.variable_layout.addWidget(self.variable_text)
        self.variable_layout.addWidget(self.variable_value)

        self.layout.setContentsMargins(
            self.edge_size*2,
            self.title_widget.height() + self.edge_size*2,
            self.edge_size*2,
            self.edge_size*2
        )
        self.layout.addWidget(self.slider)
        self.layout.addLayout(self.variable_layout)
        
        self.holder.setWidget(self.root)
   
        return None,None

    def valueChanged(self):
        """ This is called when the value of the slider changes """
        val = self.slider.value() / 100
        var_name = self.variable_text.text()
        python_code = f"{var_name} = {val}"
        self.variable_value.setText(f"{val}")
        
        # The code execution part will be added when the execution flow is merged.
        # We print for now
        print(python_code)
