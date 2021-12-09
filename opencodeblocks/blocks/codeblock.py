# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the base OCB Code Block. """

from typing import List, OrderedDict
from PyQt5.QtWidgets import QPushButton, QTextEdit

from ansi2html import Ansi2HTMLConverter
from networkx.algorithms.traversal.breadth_first_search import bfs_edges

from opencodeblocks.blocks.block import OCBBlock
from opencodeblocks.graphics.socket import OCBSocket
from opencodeblocks.graphics.pyeditor import PythonEditor

conv = Ansi2HTMLConverter()


class OCBCodeBlock(OCBBlock):

    """
    Code Block

    Features an area to edit code as well as a panel to display the output.

    The following is always true:
    output_panel_height + source_panel_height + edge_size*2 + title_height == height

    """

    def __init__(self, **kwargs):
        """
        Create a new OCBCodeBlock.
        Initialize all the child widgets specific to this block type
        """
        self.source_editor = PythonEditor(self)
        self._source = ""

        super().__init__(**kwargs)

        self.output_panel_height = self.height / 3
        self._min_output_panel_height = 20
        self._min_source_editor_height = 20

        self.output_closed = True
        self._splitter_size = [1, 1]
        self._cached_stdout = ""
        self.has_been_run = False

        # Add exectution flow sockets
        exe_sockets = (
            OCBSocket(self, socket_type="input", flow_type="exe"),
            OCBSocket(self, socket_type="output", flow_type="exe"),
        )
        for socket in exe_sockets:
            self.add_socket(socket)

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
        run_button.setFixedSize(int(3 * self.edge_size),
                                int(3 * self.edge_size))
        run_button.clicked.connect(self.run_left)
        return run_button

    def init_run_all_button(self):
        """Initialize the run all button"""
        run_all_button = QPushButton(">>", self.root)
        run_all_button.setFixedSize(
            int(3 * self.edge_size), int(3 * self.edge_size))
        run_all_button.clicked.connect(self.run_right)
        run_all_button.raise_()

        return run_all_button

    def run_code(self):
        """Run the code in the block"""
        # Reset stdout
        self._cached_stdout = ""

        # Set button text to ...
        self.run_button.setText("...")
        self.run_all_button.setText("...")

        # Run code by adding to code to queue
        code = self.source_editor.text()
        self.source = code
        kernel = self.source_editor.kernel
        kernel.execution_queue.append((self, code))
        if kernel.busy is False:
            kernel.run_queue()
        self.has_been_run = True

    def reset_buttons(self):
        """Reset the text of the run buttons"""
        self.run_button.setText(">")
        self.run_all_button.setText(">>")

    def has_input(self) -> bool:
        """Checks whether a block has connected input blocks"""
        for input_socket in self.sockets_in:
            if len(input_socket.edges) != 0:
                return True
        return False

    def has_output(self) -> bool:
        """Checks whether a block has connected output blocks"""
        for output_socket in self.sockets_out:
            if len(output_socket.edges) != 0:
                return True
        return False

    def _interrupt_execution(self):
        """ Interrupt an execution, reset the blocks in the queue """
        for block, _ in self.source_editor.kernel.execution_queue:
            # Reset the blocks that have not been run
            block.reset_buttons()
            block.has_been_run = False
        # Clear the queue
        self.source_editor.kernel.execution_queue = []
        # Interrupt the kernel
        self.source_editor.kernel.kernel_manager.interrupt_kernel()

    def run_left(self, in_right_button=False):
        """
        Run all of the block's dependencies and then run the block
        """
        # If the user presses left run when running, cancel the execution
        if self.run_button.text() == "..." and not in_right_button:
            self._interrupt_execution()
            return

        # If no dependencies
        if not self.has_input():
            return self.run_code()

        # Create the graph from the scene
        graph = self.scene().create_graph()
        # BFS through the input graph
        edges = bfs_edges(graph, self, reverse=True)
        # Run the blocks found except self
        blocks_to_run: List["OCBCodeBlock"] = [v for _, v in edges]
        for block in blocks_to_run[::-1]:
            if not block.has_been_run:
                block.run_code()

        if in_right_button:
            # If run_left was called inside of run_right
            # self is not necessarily the block that was clicked
            # which means that self does not need to be run
            if not self.has_been_run:
                self.run_code()
        else:
            # On the contrary if run_left was called outside of run_right
            # self is the block that was clicked
            # so self needs to be run
            self.run_code()

    def run_right(self):
        """Run all of the output blocks and all their dependencies"""
        # If the user presses right run when running, cancel the execution
        if self.run_all_button.text() == "...":
            self._interrupt_execution()
            return

        # If no output, run left
        if not self.has_output():
            return self.run_left(in_right_button=True)

        # Same as run_left but instead of running the blocks, we'll use run_left
        graph = self.scene().create_graph()
        edges = bfs_edges(graph, self)
        blocks_to_run: List["OCBCodeBlock"] = [
            self] + [v for _, v in edges]
        for block in blocks_to_run[::-1]:
            block.run_left(in_right_button=True)

    def reset_has_been_run(self):
        """ Reset has_been_run, is called when the output is an error """
        self.has_been_run = False

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
