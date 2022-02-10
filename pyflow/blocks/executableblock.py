# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the abstract ExecutableBlock class.

An abstract block that allows for execution, like CodeBlocks and Sliders.

"""

from typing import TYPE_CHECKING, List, OrderedDict, Set, Union
from abc import abstractmethod
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from pyflow.blocks.block import Block
from pyflow.core.socket import Socket

if TYPE_CHECKING:
    from pyflow.core.edge import Edge


class ExecutableBlock(Block):

    """
    Executable Block

    This block type is not meant to be instanciated !

    It's an abstract class that represents blocks that can be executed like:
    - CodeBlock
    - Slider

    """

    def __init__(self, **kwargs):
        """
        Create a new executable block.
        Do not call this method except when inheriting from this class.
        """
        super().__init__(**kwargs)

        self.has_been_run = False
        self._run_state = 0

        # Each element is a list of blocks/edges to be animated
        # Running will paint each element one after the other
        self.transmitting_queue = []
        # Controls the duration of the visual flow animation
        self.transmitting_duration = 500

        if type(self) == ExecutableBlock:
            raise RuntimeError("ExecutableBlock should not be instanciated directly")

    def has_input(self) -> bool:
        """Checks whether a block has connected input blocks."""
        for input_socket in self.sockets_in:
            if input_socket.edges:
                return True
        return False

    def has_output(self) -> bool:
        """Checks whether a block has connected output blocks."""
        for output_socket in self.sockets_out:
            if output_socket.edges:
                return True
        return False

    def create_new_input_socket(self) -> Socket:
        """Create a new input socket and returns it."""
        socket = Socket(self, socket_type="input", flow_type="exe")
        self.add_socket(socket)
        return socket

    def create_new_output_socket(self) -> Socket:
        """Create a new output socket and returns it."""
        socket = Socket(self, socket_type="output", flow_type="exe")
        self.add_socket(socket)
        return socket

    def run_code(self):
        """Run the code in the block."""
        # Queue the code to execute
        code = self.source
        if self.scene():
            kernel = self.scene().kernel
            kernel.execution_queue.append((self, code))

            if kernel.busy is False:
                kernel.run_queue()
            self.has_been_run = True

    def execution_finished(self):
        """Reset the text of the run buttons."""
        self.run_state = 0
        self.blocks_to_run = []

    def _interrupt_execution(self):
        """Interrupt an execution, reset the blocks in the queue."""
        for block, _ in self.scene().kernel.execution_queue:
            # Reset the blocks that have not been run
            block.reset_has_been_run()
            block.execution_finished()
        # Clear kernel execution queue
        self.scene().kernel.execution_queue = []
        # Interrupt the kernel
        self.scene().kernel.kernel_manager.interrupt_kernel()
        # Clear local execution queue
        self.blocks_to_run = []

    def transmitting_animation_in(self):
        """
        Animate the visual flow
        Set color to transmitting and set a timer before switching to normal
        """
        for elem in self.transmitting_queue[0]:
            # Set color to transmitting
            elem.run_state = 2
        QApplication.processEvents()
        QTimer.singleShot(self.transmitting_delay, self.transmitting_animation_out)

    def transmitting_animation_out(self):
        """
        Animate the visual flow
        After the timer, set color to normal and move on with the queue
        """
        for elem in self.transmitting_queue[0]:
            # Reset color only if the block will not be run
            if hasattr(elem, "has_been_run"):
                if elem.has_been_run is True:
                    elem.run_state = 0
            else:
                elem.run_state = 0

        QApplication.processEvents()
        self.transmitting_queue.pop(0)
        if self.transmitting_queue:
            # If the queue is not empty, move forward in the animation
            self.transmitting_animation_in()
        else:
            # Else, run the blocks in the self.blocks_to_run
            self.run_blocks()

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
        blocks_to_run: List["ExecutableBlock"] = []
        # List of lists of blocks/edges to animate in order
        to_transmit: List[List[Union["ExecutableBlock", "Edge"]]] = [[start_node]]

        to_visit: List["ExecutableBlock"] = [start_node]
        while to_visit:
            # Remove duplicates
            to_visit = list(set(to_visit))

            # Gather connected edges
            edges_to_visit = []
            for block in to_visit:
                blocks_to_run.append(block)
                if not reverse:
                    for input_socket in block.sockets_in:
                        for edge in input_socket.edges:
                            if (
                                edge.source_socket.is_on
                                and edge.destination_socket.is_on
                            ):
                                edges_to_visit.append(edge)
                else:
                    for output_socket in block.sockets_out:
                        for edge in output_socket.edges:
                            if (
                                edge.source_socket.is_on
                                and edge.destination_socket.is_on
                            ):
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

    def right_traversal(self):
        """
        Custom graph traversal utility
        Returns blocks/edges that will potentially be run by run_right
        from closest to farthest from self

        Returns:
            list: each element is a list of blocks/edges to animate in order
        """
        # Result
        to_transmit: List[List[Union["ExecutableBlock", "Edge"]]] = [[self]]

        # To check if a block has been visited
        visited: Set["ExecutableBlock"] = set([])
        # We need to visit the inputs of these blocks
        to_visit_input: Set["ExecutableBlock"] = set([self])
        # We need to visit the outputs of these blocks
        to_visit_output: Set["ExecutableBlock"] = set([self])

        # Next stage to put in to_transmit
        next_edges: List["Edge"] = []
        next_blocks: List["ExecutableBlock"] = []

        while to_visit_input or to_visit_output:
            for block in to_visit_input.copy():
                # Check input edges and blocks
                for input_socket in block.sockets_in:
                    for edge in input_socket.edges:
                        if not (
                            edge not in visited
                            and edge.source_socket.is_on
                            and edge.destination_socket.is_on
                        ):
                            continue
                        next_edges.append(edge)
                        visited.add(edge)
                        input_block = edge.source_socket.block
                        to_visit_input.add(input_block)
                        if input_block not in visited:
                            next_blocks.append(input_block)
                        visited.add(input_block)
                to_visit_input.remove(block)
            for block in to_visit_output.copy():
                # Check output edges and blocks
                for output_socket in block.sockets_out:
                    for edge in output_socket.edges:
                        if not (
                            edge not in visited
                            and edge.source_socket.is_on
                            and edge.destination_socket.is_on
                        ):
                            continue
                        next_edges.append(edge)
                        visited.add(edge)
                        output_block = edge.destination_socket.block
                        to_visit_input.add(output_block)
                        to_visit_output.add(output_block)
                        if output_block not in visited:
                            next_blocks.append(output_block)
                        visited.add(output_block)
                to_visit_output.remove(block)

            # Add the next stage to to_transmit
            to_transmit.append(next_edges)
            to_transmit.append(next_blocks)

            # Reset next stage
            next_edges = []
            next_blocks = []

        return to_transmit

    def run_blocks(self):
        """Run a list of blocks."""
        for block in self.blocks_to_run[::-1]:
            if not block.has_been_run:
                block.run_code()
        if not self.has_been_run:
            self.run_code()

    def run_left(self):
        """Run all of the block's dependencies and then run the block."""

        # Reset has_been_run to make sure that the self is run again
        self.has_been_run = False

        # To avoid crashing when spamming the button
        if self.transmitting_queue:
            return

        # Gather dependencies
        blocks_to_run, to_transmit = self.custom_bfs(self)
        self.blocks_to_run = blocks_to_run

        # Set the transmitting queue
        self.transmitting_queue = to_transmit
        # Set delay so that the transmitting animation has fixed total duration
        self.transmitting_delay = int(
            self.transmitting_duration / len(self.transmitting_queue)
        )
        # Start transmitting animation
        self.transmitting_animation_in()

    def run_right(self):
        """Run all of the output blocks and all their dependencies."""

        # To avoid crashing when spamming the button
        if self.transmitting_queue:
            return

        # Create transmitting queue
        self.transmitting_queue = self.right_traversal()

        # Gather outputs
        blocks_to_run, _ = self.custom_bfs(self, reverse=True)
        self.blocks_to_run = [self] + blocks_to_run

        # For each output found
        for block in self.blocks_to_run.copy()[::-1]:
            # Gather dependencies
            new_blocks_to_run, _ = self.custom_bfs(block)
            self.blocks_to_run += new_blocks_to_run

        # Set delay so that the transmitting animation has fixed total duration
        self.transmitting_delay = int(
            self.transmitting_duration / len(self.transmitting_queue)
        )
        # Start transmitting animation
        self.transmitting_animation_in()

    def reset_has_been_run(self):
        """Called when the output is an error."""
        self.has_been_run = False

    @property
    @abstractmethod
    def source(self) -> str:
        """Source code."""
        raise NotImplementedError("source(self) should be overriden")

    @source.setter
    @abstractmethod
    def source(self, value: str):
        raise NotImplementedError("source(self) should be overriden")

    @property
    def run_state(self) -> int:
        """Run state.

        Describe the current state of the ExecutableBlock:
            - 0: idle.
            - 1: running.
            - 2: transmitting.

        """
        return self._run_state

    @run_state.setter
    def run_state(self, value: int):
        self._run_state = value
        # Update to force repaint
        self.update()

    def handle_stdout(self, value: str):
        """Handle the stdout signal."""

    def handle_image(self, image: str):
        """Handle the image signal."""

    def serialize(self):
        """Return a serialized version of this block."""
        return super().serialize()

    def deserialize(
        self, data: OrderedDict, hashmap: dict = None, restore_id: bool = True
    ):
        """Restore a codeblock from it's serialized state."""
        super().deserialize(data, hashmap, restore_id)
