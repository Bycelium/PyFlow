# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the base OCB Code Block. """

from typing import OrderedDict
from PyQt5.QtWidgets import QPushButton, QTextEdit

from ansi2html import Ansi2HTMLConverter

from opencodeblocks.blocks.executableblock import OCBExecutableBlock
from opencodeblocks.graphics.socket import OCBSocket
from opencodeblocks.graphics.pyeditor import PythonEditor

conv = Ansi2HTMLConverter()


class OCBCodeBlock(OCBExecutableBlock):

    """
    Code Block

    Features an area to edit code as well as a panel to display the output.

    The following is always true:
    output_panel_height + source_panel_height + edge_size*2 + title_height == height

    """

    def __init__(self, source: str = "", **kwargs):
        """
        Create a new OCBCodeBlock.
        Initialize all the child widgets specific to this block type
        """
        super().__init__(**kwargs)
        self.source_editor = PythonEditor(self)

        self._source = ""
        self._stdout = ""

        self.source = source

        self.output_panel_height = self.height / 3
        self._min_output_panel_height = 20
        self._min_source_editor_height = 20

        self.output_closed = True
        self._splitter_size = [1, 1]

        # Add output pannel
        self.output_panel = self.init_output_panel()
        self.run_button = self.init_run_button()
        self.run_all_button = self.init_run_all_button()

        # Add splitter between source_editor and panel
        self.splitter.addWidget(self.source_editor)
        self.splitter.addWidget(self.output_panel)

        self.title_left_offset = 3 * self.edge_size

        # Build root widget into holder
        self.holder.setWidget(self.root)

        self.update_all()  # Set the geometry of display and source_editor

    def init_output_panel(self):
        """Initialize the output display widget: QLabel"""
        output_panel = QTextEdit()
        output_panel.setReadOnly(True)
        output_panel.setFont(self.source_editor.font())
        return output_panel

    def init_run_button(self):
        """Initialize the run button"""
        run_button = QPushButton(">", self.root)
        run_button.move(int(self.edge_size), int(self.edge_size / 2))
        run_button.setFixedSize(int(3 * self.edge_size), int(3 * self.edge_size))
        run_button.clicked.connect(self.handle_run_left)
        return run_button

    def init_run_all_button(self):
        """Initialize the run all button"""
        run_all_button = QPushButton(">>", self.root)
        run_all_button.setFixedSize(int(3 * self.edge_size), int(3 * self.edge_size))
        run_all_button.clicked.connect(self.handle_run_right)
        run_all_button.raise_()

        return run_all_button

    def handle_run_right(self):
        """Called when the button for "Run All" was pressed"""
        if self.is_running:
            self._interrupt_execution()
        else:
            self.run_right()

    def handle_run_left(self):
        """Called when the button for "Run Left" was pressed"""
        if self.is_running:
            self._interrupt_execution()
        else:
            self.run_left()

    def run_code(self):
        """Run the code in the block"""
        # Reset stdout
        self._cached_stdout = ""

        # Set button text to ...
        self.run_button.setText("...")
        self.run_all_button.setText("...")

        super().run_code()  # actually run the code

    def execution_finished(self):
        """Reset the text of the run buttons"""
        super().execution_finished()
        self.run_button.setText(">")
        self.run_all_button.setText(">>")

    def update_title(self):
        """Change the geometry of the title widget"""
        self.title_widget.setGeometry(
            int(self.edge_size) + self.run_button.width(),
            int(self.edge_size / 2),
            int(self.width - self.edge_size * 3 - self.run_button.width()),
            int(self.title_widget.height()),
        )

    def update_output_panel(self):
        """Change the geometry of the output panel"""
        # Close output panel if no output
        if self.stdout == "":
            self.previous_splitter_size = self.splitter.sizes()
            self.output_closed = True
            self.splitter.setSizes([1, 0])

    def update_run_all_button(self):
        """Change the geometry of the run all button"""
        self.run_all_button.move(
            int(self.width - self.edge_size - self.run_button.width()),
            int(self.edge_size / 2),
        )

    def update_all(self):
        """Update the code block parts"""
        super().update_all()
        self.update_output_panel()
        self.update_run_all_button()

    @property
    def source(self) -> str:
        """Source code"""
        return self._source

    @source.setter
    def source(self, value: str):
        if value != self._source:
            self.has_been_run = False
            self.source_editor.setText(value)
            self._source = value

    @property
    def stdout(self) -> str:
        """Access the content of the output panel of the block"""
        return self._stdout

    @stdout.setter
    def stdout(self, value: str):
        self._stdout = value
        if hasattr(self, "output_panel"):
            if value.startswith("<img>"):
                display_text = self.b64_to_html(value[5:])
            elif value.startswith("<div>"):
                display_text = value
            else:
                display_text = self.str_to_html(value)
            self.output_panel.setText(display_text)
            # If output panel is closed and there is output, open it
            if self.output_closed and value != "":
                self.output_closed = False
                self.splitter.setSizes(self._splitter_size)
            # If output panel is open and there is no output, close it
            elif not self.output_closed and value == "":
                self._splitter_size = self.splitter.sizes()
                self.output_closed = True
                self.splitter.setSizes([1, 0])

    @staticmethod
    def str_to_html(text: str):
        """Format text so that it's properly displayed by the code block"""
        # Remove carriage returns and backspaces
        text = text.replace("\x08", "")
        text = text.replace("\r", "")
        # Convert ANSI escape codes to HTML
        text = conv.convert(text)
        # Replace background color
        text = text.replace(
            "background-color: #000000", "background-color: transparent"
        )
        return text

    def handle_stdout(self, value: str):
        """Handle the stdout signal"""
        # If there is a new line
        # Save every line but the last one

        if value.find("\n") != -1:
            lines = value.split("\n")
            self._cached_stdout += "\n".join(lines[:-1]) + "\n"
            value = lines[-1]

        # Update the last line only
        self.stdout = self._cached_stdout + value

    @staticmethod
    def b64_to_html(image: str):
        """Transform a base64 encoded image into a html image"""
        return f'<img src="data:image/png;base64,{image}">'

    def handle_image(self, image: str):
        """Handle the image signal"""
        self.stdout = "<img>" + image

    def serialize(self):
        base_dict = super().serialize()
        base_dict["source"] = self.source
        base_dict["stdout"] = self.stdout
        
        return base_dict

    def deserialize(
        self, data: OrderedDict, hashmap: dict = None, restore_id: bool = True
    ):
        """Restore a codeblock from it's serialized state"""
        for dataname in ("source", "stdout"):
            if dataname in data:
                setattr(self, dataname, data[dataname])
        super().deserialize(data, hashmap, restore_id)
