# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the base OCB Code Block. """

from PyQt5.QtCore import QByteArray
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton, QTextEdit

from ansi2html import Ansi2HTMLConverter
import networkx as nx
from networkx.algorithms.dag import topological_sort
import matplotlib.pyplot as plt

from opencodeblocks.graphics.blocks.block import OCBBlock
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
        super().__init__(block_type='code', **kwargs)

        self.output_panel_height = self.height / 3
        self._min_output_panel_height = 20
        self._min_source_editor_height = 20

        self.source_editor = self.init_source_editor()
        self.output_panel = self.init_output_panel()
        self.run_button = self.init_run_button()
        self.run_right_button = self.init_run_right_button()
        self.stdout = ""
        self.image = ""
        self.title_left_offset = 3 * self.edge_size

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
                int(self.edge_size / 2),
                int(2.5 * self.edge_size),
                int(2.5 * self.edge_size)
            )
        if hasattr(self, 'run_right_button'):
            self.run_right_button.setGeometry(
                int(self.width - self.edge_size - 2.5 * self.edge_size),
                int(self.edge_size / 2),
                int(2.5 * self.edge_size),
                int(2.5 * self.edge_size)
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

            # Remove ANSI backspaces
            text = value.replace("\x08", "")
            # Convert ANSI escape codes to HTML
            text = conv.convert(text)
            # Replace background color
            text = text.replace('background-color: #000000',
                                'background-color: #434343')

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
            text = ""
            ba = QByteArray.fromBase64(str.encode(self.image))
            pixmap = QPixmap()
            pixmap.loadFromData(ba)
            text = f'<img src="data:image/png;base64,{self.image}">'
            self.output_panel.setText(text)

    @source.setter
    def source(self, value: str):
        self._source = value
        if hasattr(self, 'source_editor'):
            editor_widget = self.source_editor
            editor_widget.setText(self._source)

    def init_output_panel(self):
        """ Initialize the output display widget: QLabel """
        output_panel = QTextEdit()
        output_panel.setReadOnly(True)
        output_panel.setStyleSheet(
            "QTextEdit { background-color: #434343; }"
        )
        self.splitter.addWidget(output_panel)
        return output_panel

    def init_run_button(self):
        """ Initialize the run button """
        run_button = QPushButton(">", self.root)
        run_button.setMinimumWidth(int(self.edge_size))
        run_button.clicked.connect(self.run_left)
        run_button.raise_()

        return run_button

    def init_run_right_button(self):
        """ Initialize the run all button """
        run_all_button = QPushButton(">>", self.root)
        run_all_button.setMinimumWidth(int(self.edge_size))
        run_all_button.clicked.connect(self.run_right)
        run_all_button.raise_()

        return run_all_button

    def run_left(self):
        """
        Runs the block and every block connected to its input
        in topological order
        """
        graph = self.create_graph([], self, "left")
        block_generator = topological_sort(graph)
        kernel = self.source_editor.kernel
        for block in block_generator:
            kernel.execution_queue.append((block, block.source))
        if kernel.busy == False:
            kernel.run_queue()

    def run_right(self):
        """
        Runs the block and every block connected to its output
        in topological order
        """
        self.run_left()
        graph = self.create_graph([], self, "right")
        block_generator = topological_sort(graph)
        kernel = self.source_editor.kernel
        for block in block_generator:
            kernel.execution_queue.append((block, block.source))
        if kernel.busy == False:
            kernel.run_queue()

    def gather_output_blocks(self):
        """
        Check all output sockets for connected blocks and return a list of
        connected blocks.
        """
        output_blocks = []
        for output_socket in self.sockets_out:
            if output_socket.edges != []:
                for edge in output_socket.edges:
                    output_blocks.append(edge.destination_socket.block)
        return output_blocks

    def gather_input_blocks(self):
        """
        Check all input sockets for connected blocks and return a list of
        connected blocks.
        """
        input_blocks = []
        for input_socket in self.sockets_in:
            if input_socket.edges != []:
                for edge in input_socket.edges:
                    input_blocks.append(edge.source_socket.block)
        return input_blocks

    def create_graph(self, explored_blocks, source, direction):
        """
        Browse all of the connected blocks recursively
        and create a directed graph

        Args:
            explored_blocks: list of blocks already explored
            source: the initial block
            direction: "left" or "right"
                if "left", the graph is built from the output blocks of source
                if "right", the graph is built from the input blocks of source

        Returns:
            graph: a directed NetworkX graph
        """

        graph = nx.DiGraph()
        graph.add_node(self)
        if self not in explored_blocks:
            explored_blocks.append(self)
            if not (self == source and direction == "left"):
                for block in self.gather_output_blocks():
                    graph.add_node(block)
                    graph.add_edge(self, block)
                    graph.add_edges_from(block.create_graph(
                        explored_blocks, source, direction).edges)

            if not (self == source and direction == "right"):
                for block in self.gather_input_blocks():
                    graph.add_node(block)
                    graph.add_edge(block, self)
                    graph.add_edges_from(block.create_graph(
                        explored_blocks, source, direction).edges)

        return graph

    def plot_graph(self, graph):
        """
        Plot a graph using matplotlib
        """
        pos = nx.spring_layout(graph)
        labels = {}
        for node in graph.nodes:
            labels[node] = node.title
        nx.draw(graph, pos, labels=labels, font_size=8, node_size=500)
        plt.show()

    def handle_stdout(self, stdout):
        """ Handle the stdout signal """
        self.stdout = stdout

    def handle_image(self, image):
        """ Handle the image signal """
        self.image = image
