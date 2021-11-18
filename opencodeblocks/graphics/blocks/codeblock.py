# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the base OCB Code Block. """


import re

from PyQt5.QtCore import QCoreApplication, QByteArray
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton


from opencodeblocks.graphics.blocks.block import OCBBlock
from opencodeblocks.graphics.pyeditor import PythonEditor

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


class OCBCodeBlock(OCBBlock):

    """
    Code Block

    Features an area to edit code as well as a panel to display the output.

    The following is always true:
    output_panel_height + source_panel_height + edge_size*2 + title_height == height

    """

    def __init__(self, **kwargs):
        super().__init__(block_type='code', **kwargs)

        self.output_panel_height = self.height / 3
        self._min_output_panel_height = 20
        self._min_source_editor_height = 20

        self.source_editor = self.init_source_editor()
        self.output_panel = self.init_output_panel()
        self.run_button = self.init_run_button()
        self.stdout = ""
        self.image = ""

        self.holder.setWidget(self.root)

        self.update_all()  # Set the geometry of display and source_editor

    def init_source_editor(self):
        """ Initialize the python source code editor. """
        source_editor = PythonEditor(self)
        self.splitter.addWidget(source_editor)
        return source_editor

    def update_all(self):
        """ Update the code block parts. """
        super().update_all()
        if hasattr(self, 'run_button'):
            self.run_button.setGeometry(
                int(self.edge_size),
                int(self.edge_size + self.title_height),
                int(2.5*self.edge_size),
                int(2.5*self.edge_size)
            )

    @property
    def source(self) -> str:
        """ Source code. """
        return self._source

    @source.setter
    def source(self, value: str):
        self._source = value
        if hasattr(self, 'source_editor'):
            self.source_editor.setText(self._source)

    @property
    def stdout(self) -> str:
        """ Code output. Be careful, this also includes stderr """
        return self._stdout

    @stdout.setter
    def stdout(self, value: str):
        self._stdout = value
        if hasattr(self, 'source_editor'):
            # If there is a text output, erase the image output and display the
            # text output
            self.image = ""

            # Remove ANSI color codes
            text = ansi_escape.sub('', value)
            # Remove backspaces (tf loading bars)
            text = text.replace('\x08', '')
            self.output_panel.setText(text)

    @property
    def image(self) -> str:
        """ Code output. """
        return self._image

    @image.setter
    def image(self, value: str):
        self._image = value
        if hasattr(self, 'source_editor') and self.image != "":
            # If there is an image output, erase the text output and display
            # the image output
            self.output_panel.setText("")
            ba = QByteArray.fromBase64(str.encode(self.image))
            pixmap = QPixmap()
            pixmap.loadFromData(ba)
            self.output_panel.setPixmap(pixmap)

    @source.setter
    def source(self, value: str):
        self._source = value
        if hasattr(self, 'source_editor'):
            editor_widget = self.source_editor
            editor_widget.setText(self._source)


    def init_output_panel(self):
        """ Initialize the output display widget: QLabel """
        output_panel = QLabel()
        output_panel.setText("")

        self.splitter.addWidget(output_panel)
        return output_panel

    def init_run_button(self):
        """ Initialize the run button """
        run_button = QPushButton(">",self.root)
        run_button.setMinimumWidth(int(self.edge_size))
        run_button.clicked.connect(self.run_code)
        run_button.raise_()

        return run_button

    def run_code(self):
        """Run the code in the block"""
        code = self.source_editor.text()
        kernel = self.source_editor.kernel
        self.source = code
        # Execute the code
        kernel.client.execute(code)
        done = False
        # While the kernel sends messages
        while done is False:
            # Keep the GUI alive
            QCoreApplication.processEvents()
            # Save kernel message and display it
            output, output_type, done = kernel.update_output()
            if done is False:
                if output_type == 'text':
                    self.stdout = output
                elif output_type == 'image':
                    self.image = output
