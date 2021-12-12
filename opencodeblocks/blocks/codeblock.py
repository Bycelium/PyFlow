# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the base OCB Code Block. """

from typing import OrderedDict, Optional
from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QTextEdit,
    QWidget,
    QStyleOptionGraphicsItem,
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPen, QColor, QPainter, QPainterPath

from ansi2html import Ansi2HTMLConverter

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

        self._pen_outline = QPen(QColor("#7F000000"))
        self._pen_outline_running = QPen(QColor("#FF0000"))
        self._pen_outline_transmitting = QPen(QColor("#00ff00"))
        self._pen_outlines = [
            self._pen_outline,
            self._pen_outline_running,
            self._pen_outline_transmitting,
        ]
        # 0 for normal, 1 for running, 2 for transmitting
        self.run_color = 0

        # Each element is a list of blocks/edges to be animated
        # Running will paint each element one after the other
        self.transmitting_queue = []
        # Controls the duration of the visual flow animation
        self.transmitting_duration = 500
        self.transmitting_delay = 200

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
        run_button.setFixedSize(int(3 * self.edge_size), int(3 * self.edge_size))
        run_button.clicked.connect(self.run_left)
        return run_button

    def init_run_all_button(self):
        """Initialize the run all button"""
        run_all_button = QPushButton(">>", self.root)
        run_all_button.setFixedSize(int(3 * self.edge_size), int(3 * self.edge_size))
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

    def reset_after_run(self):
        """Reset buttons and color after a run"""
        self.run_color = 0
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
        """Interrupt an execution, reset the blocks in the queue"""
        for block, _ in self.source_editor.kernel.execution_queue:
            # Reset the blocks that have not been run
            block.reset_after_run()
            block.has_been_run = False
        # Clear the queue
        self.source_editor.kernel.execution_queue = []
        # Interrupt the kernel
        self.source_editor.kernel.kernel_manager.interrupt_kernel()

    def transmitting_animation_in(self):
        """
        Animate the visual flow
        Set color to transmitting and set a timer before switching to normal
        """
        for elem in self.transmitting_queue[0]:
            elem.run_color = 2
        QApplication.processEvents()
        QTimer.singleShot(self.transmitting_delay, self.transmitting_animation_out)

    def transmitting_animation_out(self):
        """
        Animate the visual flow
        After the timer, set color to normal and move on with the queue
        """
        for elem in self.transmitting_queue[0]:
            elem.run_color = 0
        QApplication.processEvents()
        self.transmitting_queue.pop(0)
        if len(self.transmitting_queue) != 0:
            self.transmitting_animation_in()

    def custom_bfs(self, start_node, reverse=False):
        """
        Graph traversal in BFS to find the blocks that are connected to the start_node

        Args:
            start_node (Block): The block to start the traversal from
            reverse (bool): If True, traverse in the direction of outputs

        Returns:
            list: Blocks to run in topological order (reversed)
            list: each element is a list of blocks/edges to animate in order
        """
        # Blocks to run in topological order
        blocks_to_run = []
        # List of lists of blocks/edges to animate in order
        to_transmit = [[start_node]]

        to_visit = [start_node]
        while len(to_visit) != 0:
            # Remove duplicates
            to_visit = list(set(to_visit))

            # Gather connected edges
            edges_to_visit = []
            for block in to_visit:
                blocks_to_run.append(block)
                if not reverse:
                    for input_socket in block.sockets_in:
                        for edge in input_socket.edges:
                            edges_to_visit.append(edge)
                else:
                    for output_socket in block.sockets_out:
                        for edge in output_socket.edges:
                            edges_to_visit.append(edge)
            to_transmit.append(edges_to_visit)

            # Gather connected blocks
            to_visit = []
            for edge in edges_to_visit:
                if not reverse:
                    to_visit.append(edge.source_socket.block)
                else:
                    to_visit.append(edge.destination_socket.block)
            to_transmit.append(to_visit)

        # Remove start node
        blocks_to_run.pop(0)

        return blocks_to_run, to_transmit

    def run_blocks(self, blocks_to_run):
        """Run a list of blocks"""
        for block in blocks_to_run[::-1]:
            if not block.has_been_run:
                block.run_code()

    def run_left(self):
        """Run all of the block's dependencies and then run the block"""

        # To avoid crashing when spamming the button
        if len(self.transmitting_queue) != 0:
            return

        # If the user presses left run when running, cancel the execution
        if self.run_button.text() == "...":
            self._interrupt_execution()
            return

        # Gather dependencies
        blocks_to_run, to_transmit = self.custom_bfs(self)

        # Set the transmitting queue
        self.transmitting_queue = to_transmit
        # Set delay so that the transmitting animation has fixed total duration
        self.transmitting_delay = int(
            self.transmitting_duration / len(self.transmitting_queue)
        )
        # Start transmitting animation
        self.transmitting_animation_in()

        # Run the blocks
        self.run_blocks(blocks_to_run)

        # Run self
        self.run_code()

    def run_right(self):
        """Run all of the output blocks and all their dependencies"""

        # To avoid crashing when spamming the button
        if len(self.transmitting_queue) != 0:
            return

        # If the user presses right run when running, cancel the execution
        if self.run_all_button.text() == "...":
            self._interrupt_execution()
            return

        # Gather outputs
        blocks_to_run, to_transmit = self.custom_bfs(self, reverse=True)

        # Init transmitting queue
        self.transmitting_queue = to_transmit

        # For each output found
        for block in blocks_to_run[::-1]:
            # Gather dependencies
            new_blocks_to_run, new_to_transmit = self.custom_bfs(block)
            blocks_to_run += new_blocks_to_run
            self.transmitting_queue += new_to_transmit

        # Set delay so that the transmitting animation has fixed total duration
        self.transmitting_delay = int(
            self.transmitting_duration / len(self.transmitting_queue)
        )
        # Start transmitting animation
        self.transmitting_animation_in()

        # Run the blocks
        self.run_blocks(blocks_to_run)

    def reset_has_been_run(self):
        """Reset has_been_run, is called when the output is an error"""
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

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ):
        """Paint the code block"""
        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addRoundedRect(
            0, 0, self.width, self.height, self.edge_size, self.edge_size
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(
            0, 0, self.width, self.height, self.edge_size, self.edge_size
        )
        painter.setPen(
            self._pen_outline_selected
            if self.isSelected()
            else self._pen_outlines[self.run_color]
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path_outline.simplified())

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
    def run_color(self) -> int:
        """Run color"""
        return self._run_color

    @run_color.setter
    def run_color(self, value: int):
        self._run_color = value
        # Update to force repaint
        self.update()

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
        """Serialize the code block"""
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
