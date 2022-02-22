# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the base Code Block."""

from typing import TYPE_CHECKING, OrderedDict, Tuple

from ansi2html import Ansi2HTMLConverter
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QPushButton, QTextEdit

from pyflow.blocks.block import Block
from pyflow.core.edge import Edge
from pyflow.blocks.executableblock import ExecutableBlock, ExecutableState
from pyflow.blocks.pyeditor import PythonEditor
from pyflow.core.add_button import AddEdgeButton, AddNewBlockButton

ansi2html_converter = Ansi2HTMLConverter()

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QGraphicsSceneHoverEvent


class CodeBlock(ExecutableBlock):

    """
    Code Block

    Features an area to edit code as well as a panel to display the output.

    The following is always true:
    output_panel_height + source_panel_height + edge_size*2 + title_height == height

    """

    DEFAULT_DATA = {
        **Block.DEFAULT_DATA,
        "source": "",
    }
    MANDATORY_FIELDS = Block.MANDATORY_FIELDS

    def __init__(self, source: str = "", **kwargs):

        """
        Create a new CodeBlock.
        Initialize all the child widgets specific to this block type.

        """

        super().__init__(block_type="CodeBlock", **kwargs)
        self.source_editor = PythonEditor(self)

        self._source = ""
        self._stdout = ""

        self.source = source

        self.output_panel_height = self.height / 3
        self._min_output_panel_height = 20
        self._min_source_editor_height = 20

        self.output_closed = True
        self._splitter_size = [1, 1]
        self._cached_stdout = ""
        self.blocks_to_run = []

        self._pen_outlines = {
            ExecutableState.IDLE: QPen(QColor("#00000000")),  # No outline
            ExecutableState.RUNNING: QPen(QColor("#fffc6107")),  # Dark orange
            ExecutableState.PENDING: QPen(QColor("#90fc6107")),  # Transparent orange
            ExecutableState.DONE: QPen(QColor("#158000")),  # Dark green
            ExecutableState.CRASHED: QPen(QColor("#ff0000")),  # Red: Crashed
        }
        for pen in self._pen_outlines.values():
            pen.setWidth(self.pen_width)

        self.output_panel_background_color = "#1E1E1E"

        # Add output pannel
        self.output_panel = self.init_output_panel()
        self.run_button = self.init_run_button()
        self.run_all_button = self.init_run_all_button()
        self.add_edge_button = self.init_add_edge_button()
        self.add_newblock_button = self.init_add_newblock_button()

        # Add splitter between source_editor and panel
        self.splitter.addWidget(self.source_editor)
        self.splitter.addWidget(self.output_panel)

        self.title_left_offset = 3 * self.edge_size

        # Build root widget into holder
        self.holder.setWidget(self.root)

        self.setAcceptHoverEvents(True)

        self.update_all()  # Set the geometry of display and source_editor

    def init_output_panel(self):
        """Initialize the output display widget: QLabel."""
        output_panel = QTextEdit()
        output_panel.setReadOnly(True)
        output_panel.setFont(self.source_editor.font())
        style_sheet = (
            f'QTextEdit {{ background-color: "{self.output_panel_background_color}"; }}'
        )
        output_panel.setStyleSheet(style_sheet)
        return output_panel

    def init_run_button(self):
        """Initialize the run button."""
        run_button = QPushButton(">", self.root)
        run_button.move(int(self.edge_size), int(self.edge_size / 2))
        run_button.setFixedSize(int(3 * self.edge_size), int(3 * self.edge_size))
        run_button.clicked.connect(self.handle_run_left)
        return run_button

    def init_run_all_button(self):
        """Initialize the run all button."""
        run_all_button = QPushButton(">>", self.root)
        run_all_button.setFixedSize(int(3 * self.edge_size), int(3 * self.edge_size))
        run_all_button.clicked.connect(self.handle_run_right)
        run_all_button.raise_()

        return run_all_button

    def init_add_edge_button(self):
        """Initialize the add edge button."""
        add_edge_button = AddEdgeButton(block=self)
        return add_edge_button

    def init_add_newblock_button(self):
        """Initialize the add a new block button."""
        add_newblock_button = AddNewBlockButton(block=self)
        return add_newblock_button

    def handle_run_right(self):
        """Called when the button for "Run All" was pressed."""
        if self.run_state in (ExecutableState.PENDING, ExecutableState.RUNNING):
            self._interrupt_execution()
        else:
            self.run_right()

    def handle_run_left(self):
        """Called when the button for "Run Left" was pressed."""
        if self.run_state in (ExecutableState.PENDING, ExecutableState.RUNNING):
            self._interrupt_execution()
        else:
            self.run_left()

    def hoverEnterEvent(self, event: "QGraphicsSceneHoverEvent") -> None:
        """Handle the event when the mouse enters the block."""
        self.add_edge_button.set_highlight(True)
        self.add_newblock_button.set_highlight(True)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: "QGraphicsSceneHoverEvent") -> None:
        """Handle the event when the mouse leaves the block."""
        self.add_edge_button.set_highlight(False)
        self.add_newblock_button.set_highlight(False)
        return super().hoverLeaveEvent(event)

    def run_code(self):
        """Run the code in the block."""

        # Reset stdout
        self._cached_stdout = ""

        # Set button text to ...
        self.run_button.setText("...")
        self.run_all_button.setText("...")

        super().run_code()  # actually run the code

    def execution_finished(self):
        """Reset the text of the run buttons after it was executed."""
        super().execution_finished()
        self.run_button.setText(">")
        self.run_all_button.setText(">>")

    def execution_canceled(self):
        """Reset the text of the run buttons after it was canceled."""
        super().execution_canceled()
        self.run_button.setText(">")
        self.run_all_button.setText(">>")

    def link(self, block: "ExecutableBlock"):
        """Link a block to the current one."""
        # Add sockets to the new block and the current one
        source_socket = self.create_new_output_socket()
        destination_socket = block.create_new_input_socket()

        # Create an edge between the two blocks
        edge = Edge(source_socket=source_socket, destination_socket=destination_socket)
        self.scene().addItem(edge)

    def place(self, block: Block, horizontal_direction: str, vertical_direction: str):
        """Place a block under itself.

        horizontal_direction is a string in {"left", "mid", "right"}
        vertical_direction is a string in {"up", "down"}
        that says where to place the block relative to this block."""
        block.setPos(self.pos().x(), self.pos().y())

        delta_x: float = self.width + 20
        if horizontal_direction == "left":
            block.setPos(block.pos().x() - delta_x, block.pos().y())
        elif horizontal_direction == "right":
            block.setPos(block.pos().x() + delta_x, block.pos().y())
        elif horizontal_direction != "mid":
            raise ValueError("invalid horizontal direction ", horizontal_direction)

        delta_y = self.height + 100
        if vertical_direction == "up":
            block.setPos(block.pos().x(), block.pos().y() - delta_y)
        elif vertical_direction == "down":
            block.setPos(block.pos().x(), block.pos().y() + delta_y)
        else:
            raise ValueError("invalid vertical direction ", vertical_direction)

    def link_and_place(self, block: "CodeBlock", direction: Tuple[str, str]):
        """Create a new linked block in the right direction."""

        vertical_direction, horizontal_direction = direction

        self.place(block, horizontal_direction, vertical_direction)

        if vertical_direction == "up":
            block.link(self)
        elif vertical_direction == "down":
            self.link(block)
        else:
            raise ValueError("invalid link direction ", vertical_direction)

        self.update_sockets()

    def update_title(self):
        """Change the geometry of the title widget."""
        self.title_widget.setGeometry(
            int(self.edge_size) + self.run_button.width(),
            int(self.edge_size / 2),
            int(self.width - self.edge_size * 3 - self.run_button.width()),
            int(self.title_widget.height()),
        )

    def update_output_panel(self):
        """Change the geometry of the output panel."""
        # Close output panel if no output
        if self.stdout == "":
            self.previous_splitter_size = self.splitter.sizes()
            self.output_closed = True
            self.splitter.setSizes([1, 0])

    def update_run_all_button(self):
        """Change the geometry of the run all button."""
        self.run_all_button.move(
            int(self.width - self.edge_size - self.run_button.width()),
            int(self.edge_size / 2),
        )

    def get_add_edge_button_pos(self) -> Tuple[int, int]:
        """Get the position where to place the add edge button."""
        return (
            self.width / 2,
            self.height
            + int(2.5 * self.add_edge_button.radius)
            + int(2.5 * self.add_newblock_button.radius),
        )

    def get_add_newblock_button_pos(self) -> Tuple[int, int]:
        """Get the position where to place the add newblock button."""
        return (
            self.width / 2,
            self.height + int(2.5 * self.add_newblock_button.radius),
        )

    def update_add_edge_button(self):
        """Change the geometry of the add edge button."""
        self.add_edge_button.setPos(*self.get_add_edge_button_pos())

    def update_add_newblock_button(self):
        """Change the geometry of the add newblock button."""
        self.add_newblock_button.setPos(*self.get_add_newblock_button_pos())

    def update_all(self):
        """Update the code block parts."""
        super().update_all()
        self.update_output_panel()
        self.update_run_all_button()
        self.update_add_edge_button()
        self.update_add_newblock_button()

    @property
    def source(self) -> str:
        """Source code."""
        return self.source_editor.text()

    @source.setter
    def source(self, value: str):
        if value != self._source:
            # If text has changed, set self and all output blocks to not run
            output_blocks, _ = self.custom_bfs(self, reverse=True)
            for block in output_blocks + [self]:
                block.run_state = ExecutableState.IDLE
            self.source_editor.setText(value)
            self._source = value

    @property
    def pen_outline(self) -> QPen:
        """The current pen used to draw the outline of the CodeBlock."""
        return self._pen_outlines[self.run_state]

    @property
    def stdout(self) -> str:
        """Access the content of the output panel of the block."""
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
    def str_to_html(text: str) -> str:
        """Format text so that it's properly displayed by the code block."""
        # Remove carriage returns and backspaces
        text = text.replace("\x08", "")
        text = text.replace("\r", "")
        # Convert ANSI escape codes to HTML
        text = ansi2html_converter.convert(text)
        # Replace background color
        text = text.replace(
            "background-color: #000000", "background-color: transparent"
        )
        return text

    def handle_stdout(self, value: str):
        """Handle the stdout signal."""
        # If there is a new line
        # Save every line but the last one

        if value.find("\n") != -1:
            lines = value.split("\n")
            self._cached_stdout += "\n".join(lines[:-1]) + "\n"
            value = lines[-1]

        # Update the last line only
        self.stdout = self._cached_stdout + value

    @staticmethod
    def b64_to_html(image: str) -> str:
        """Transform a base64 encoded image into a html image."""
        return f'<img src="data:image/png;base64,{image}">'

    def handle_image(self, image: str):
        """Handle the image signal."""
        self.stdout = "<img>" + image

    def serialize(self):
        """Serialize the code block."""
        base_dict = super().serialize()
        base_dict["source"] = self.source
        base_dict["stdout"] = self.stdout
        return base_dict

    def deserialize(
        self, data: OrderedDict, hashmap: dict = None, restore_id: bool = True
    ):
        """Restore a codeblock from it's serialized state."""

        self.complete_with_default(data)

        for dataname in ("source", "stdout"):
            if dataname in data:
                setattr(self, dataname, data[dataname])
        super().deserialize(data, hashmap, restore_id)
