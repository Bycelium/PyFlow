# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the abstract ExecutableBlock class.

An abstract block that allows for execution, like CodeBlocks and Sliders.

"""

from typing import List, OrderedDict, Set, Union
from abc import abstractmethod
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from pyflow.blocks.block import Block
from pyflow.core.socket import Socket
from pyflow.core.edge import Edge
from pyflow.core.executable import Executable, ExecutableState


class ExecutableBlock(Block, Executable):

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
        Block.__init__(self, **kwargs)
        Executable.__init__(self)

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
            self.run_state = ExecutableState.PENDING

    def execution_finished(self):
        """Reset the state of the block after it was executed."""
        if self.run_state != ExecutableState.CRASHED:
            self.run_state = ExecutableState.DONE
        self.blocks_to_run = []

    def execution_canceled(self):
        """Reset the state of the block after its execution was canceled."""
        if self.run_state != ExecutableState.CRASHED:
            self.run_state = ExecutableState.IDLE
        self.blocks_to_run = []

    def _interrupt_execution(self):
        """Interrupt an execution, reset the blocks in the queue."""
        for block, _ in self.scene().kernel.execution_queue:
            # Reset the blocks that have not been run
            block.execution_canceled()
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
        QApplication.processEvents()
        QTimer.singleShot(self.transmitting_delay, self.transmitting_animation_out)

    def transmitting_animation_out(self):
        """
        Animate the visual flow
        After the timer, set color to normal and move on with the queue
        """
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

        def gather_edges_to_visit(sockets: List[Socket]):
            """Get list of next edges to visit given a list of sockets.

            Args:
                sockets (List[Socket]): List of sockets to search edges on.

            Returns:
                List[Edge]: List of edges connected to sockets given.
            """
            edges_to_visit = []
            for socket in sockets:
                for edge in socket.edges:
                    if edge.source_socket.is_on and edge.destination_socket.is_on:
                        edges_to_visit.append(edge)
            return edges_to_visit

        # Blocks to run in topological order
        blocks_to_run: List["ExecutableBlock"] = []
        # List of lists of blocks/edges to animate in order
        to_transmit: List[List[Union["ExecutableBlock", Edge]]] = [[start_node]]

        # Set to make sure to never execute the same block twice
        visited: Set["ExecutableBlock"] = set([])

        blocks_to_visit: List["ExecutableBlock"] = [start_node]
        while blocks_to_visit:
            # Remove duplicates
            blocks_to_visit = list(set(blocks_to_visit))

            # Remove duplicates
            to_visit_set = set(blocks_to_visit)
            to_visit_set.difference_update(visited)
            blocks_to_visit = list(to_visit_set)

            # Update the visited block set
            visited.update(to_visit_set)

            # Gather connected edges
            edges_to_visit: List[Edge] = []
            for block in blocks_to_visit:
                blocks_to_run.append(block)
                if not reverse:
                    next_sockets = block.sockets_in
                else:
                    next_sockets = block.sockets_out
                edges_to_visit += gather_edges_to_visit(next_sockets)
            to_transmit.append(edges_to_visit)

            # Gather connected blocks
            blocks_to_visit = []
            for edge in edges_to_visit:
                if not reverse:
                    next_blocks = edge.source_socket.block
                else:
                    next_blocks = edge.destination_socket.block
                blocks_to_visit.append(next_blocks)
            to_transmit.append(blocks_to_visit)

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

        def gather_next_blocks_and_edges(
            sockets: List[Socket],
            visited: Set[Union[Block, Edge]] = None,
            to_visit: Set[Block] = None,
        ):
            """Gather next blocks and edges to run given a list of sockets.

            Args:
                sockets (List[Socket]): List of sockets to search next blocks and edges on.
                visited (Set[Union[Block, Edge]], optional): Already visited blocks and edges. Defaults to None.
                to_visit (Set[Block], optional): List of next blocks to visit. Defaults to None.

            Returns:
                Tuple[List[Block], List[Edge]]: Lists of next blocks and next edges to run.
            """
            visited = set() if visited is None else visited
            to_visit = set() if to_visit is None else to_visit

            next_blocks = []
            next_edges = []

            for socket in sockets:
                for edge in socket.edges:
                    if not (
                        edge not in visited
                        and edge.source_socket.is_on
                        and edge.destination_socket.is_on
                    ):
                        continue

                    next_edges.append(edge)
                    visited.add(edge)

                    next_block = edge.destination_socket.block
                    to_visit.add(next_block)
                    visited.add(next_block)

                    if next_block not in visited:
                        next_blocks.append(next_block)

            return next_blocks, next_edges

        # Result
        to_transmit: List[List[Union["ExecutableBlock", Edge]]] = [[self]]

        # To check if a block has been visited
        visited: Set["ExecutableBlock"] = set([])
        # We need to visit the inputs of these blocks
        to_visit_input: Set["ExecutableBlock"] = set([self])
        # We need to visit the outputs of these blocks
        to_visit_output: Set["ExecutableBlock"] = set([self])

        # Next stage to put in to_transmit
        next_edges: List[Edge] = []
        next_blocks: List["ExecutableBlock"] = []

        while to_visit_input or to_visit_output:
            for block in to_visit_input.copy():
                # Check input edges and blocks
                new_blocks, new_edges = gather_next_blocks_and_edges(
                    block.sockets_in, visited, to_visit_input
                )
                next_blocks += new_blocks
                next_edges += new_edges
                to_visit_input.remove(block)
            for block in to_visit_output.copy():
                # Check output edges and blocks
                new_blocks, new_edges = gather_next_blocks_and_edges(
                    block.sockets_out, visited, to_visit_output
                )
                next_blocks += new_blocks
                next_edges += new_edges
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
        for block in self.blocks_to_run[::-1] + [self]:
            if block.run_state not in {
                ExecutableState.PENDING,
                ExecutableState.RUNNING,
                ExecutableState.DONE,
            }:
                block.run_code()

    def run_left(self):
        """Run all of the block's dependencies and then run the block."""

        # Reset state to make sure that the self is run again
        self.run_state = ExecutableState.IDLE

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
            if block is not self:
                block.run_state = ExecutableState.IDLE
            new_blocks_to_run, _ = self.custom_bfs(block)
            self.blocks_to_run += new_blocks_to_run

        # Set delay so that the transmitting animation has fixed total duration
        self.transmitting_delay = int(
            self.transmitting_duration / len(self.transmitting_queue)
        )
        # Start transmitting animation
        self.transmitting_animation_in()

    def error_occured(self):
        """Interrupt the kernel if an error occured"""
        self.run_state = ExecutableState.CRASHED
        self._interrupt_execution()

    @property
    @abstractmethod
    def source(self) -> str:
        """Source code."""
        raise NotImplementedError("source(self) should be overriden")

    @source.setter
    @abstractmethod
    def source(self, value: str):
        raise NotImplementedError("source(self) should be overriden")

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
