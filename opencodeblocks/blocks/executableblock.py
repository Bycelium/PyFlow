""" Module for the executable block class """

from typing import OrderedDict
from abc import abstractmethod
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from networkx.algorithms.traversal.breadth_first_search import bfs_edges

from opencodeblocks.blocks.block import OCBBlock
from opencodeblocks.graphics.socket import OCBSocket


class OCBExecutableBlock(OCBBlock):

    """
    Executable Block

    This block type is not meant to be instanciated !

    It's an abstract class that represents blocks that can be executed like:
    - OCBCodeBlock
    - OCBSlider

    """

    def __init__(self, **kwargs):
        """
        Create a new executable block.
        Do not call this method except when inheriting from this class.
        """
        super().__init__(**kwargs)

        self.has_been_run = False

        # 0 for normal, 1 for running, 2 for transmitting
        self.run_color = 0

        # Each element is a list of blocks/edges to be animated
        # Running will paint each element one after the other
        self.transmitting_queue = []
        # Controls the duration of the visual flow animation
        self.transmitting_duration = 500

        # Add execution flow sockets
        exe_sockets = (
            OCBSocket(self, socket_type="input", flow_type="exe"),
            OCBSocket(self, socket_type="output", flow_type="exe"),
        )
        for socket in exe_sockets:
            self.add_socket(socket)

        if type(self) == OCBExecutableBlock:
            raise RuntimeError("OCBExecutableBlock should not be instanciated directly")

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

    def run_code(self):
        """Run the code in the block"""

        # Queue the code to execute
        code = self.source
        kernel = self.scene().kernel
        kernel.execution_queue.append((self, code))

        if kernel.busy is False:
            kernel.run_queue()
        self.has_been_run = True

    def execution_finished(self):
        """Reset the text of the run buttons"""
        self.run_color = 0
        self.run_button.setText(">")
        self.run_all_button.setText(">>")
        self.blocks_to_run = []

    def _interrupt_execution(self):
        """Interrupt an execution, reset the blocks in the queue"""
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
            elem.run_color = 2
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
                    elem.run_color = 0
            else:
                elem.run_color = 0

        QApplication.processEvents()
        self.transmitting_queue.pop(0)
        if len(self.transmitting_queue) != 0:
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

    def right_traversal(self):
        """
        Custom graph traversal utility
        Returns blocks/edges that will potentially be run by run_right
        from closest to farthest from self

        Returns:
            list: each element is a list of blocks/edges to animate in order
        """
        # Result
        to_transmit = [[self]]

        # To check if a block has been visited
        visited = []
        # We need to visit the inputs of these blocks
        to_visit_input = [self]
        # We need to visit the outputs of these blocks
        to_visit_output = [self]

        # Next stage to put in to_transmit
        next_edges = []
        next_blocks = []

        while len(to_visit_input) != 0 or len(to_visit_output) != 0:
            for block in to_visit_input.copy():
                # Check input edges and blocks
                for input_socket in block.sockets_in:
                    for edge in input_socket.edges:
                        if edge not in visited:
                            next_edges.append(edge)
                        visited.append(edge)
                        input_block = edge.source_socket.block
                        to_visit_input.append(input_block)
                        if input_block not in visited:
                            next_blocks.append(input_block)
                        visited.append(input_block)
                to_visit_input.remove(block)
            for block in to_visit_output.copy():
                # Check output edges and blocks
                for output_socket in block.sockets_out:
                    for edge in output_socket.edges:
                        if edge not in visited:
                            next_edges.append(edge)
                        visited.append(edge)
                        output_block = edge.destination_socket.block
                        to_visit_input.append(output_block)
                        to_visit_output.append(output_block)
                        if output_block not in visited:
                            next_blocks.append(output_block)
                        visited.append(output_block)
                to_visit_output.remove(block)

            # Add the next stage to to_transmit
            to_transmit.append(next_edges)
            to_transmit.append(next_blocks)

            # Reset next stage
            next_edges = []
            next_blocks = []

        return to_transmit

    def run_blocks(self):
        """Run a list of blocks"""
        for block in self.blocks_to_run[::-1]:
            if not block.has_been_run:
                block.run_code()
        if not self.has_been_run:
            self.run_code()

    def run_left(self):
        """Run all of the block's dependencies and then run the block"""

        # Reset has_been_run to make sure that the self is run again
        self.has_been_run = False

        # To avoid crashing when spamming the button
        if len(self.transmitting_queue) != 0:
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
        """Run all of the output blocks and all their dependencies"""

        # To avoid crashing when spamming the button
        if len(self.transmitting_queue) != 0:
            return

        # Create transmitting queue
        self.transmitting_queue = self.right_traversal()

        # Gather outputs
        blocks_to_run, _ = self.custom_bfs(self, reverse=True)
        self.blocks_to_run = blocks_to_run

        # For each output found
        for block in blocks_to_run.copy()[::-1]:
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
        """Called when the output is an error"""
        self.has_been_run = False

    @property
    @abstractmethod
    def source(self) -> str:
        """Source code"""
        raise NotImplementedError("source(self) should be overriden")

    @source.setter
    @abstractmethod
    def source(self, value: str):
        raise NotImplementedError("source(self) should be overriden")

    def handle_stdout(self, value: str):
        """Handle the stdout signal"""

    def handle_image(self, image: str):
        """Handle the image signal"""

    def serialize(self):
        """Return a serialized version of this block"""
        return super().serialize()

    def deserialize(
        self, data: OrderedDict, hashmap: dict = None, restore_id: bool = True
    ):
        """Restore a codeblock from it's serialized state"""
        super().deserialize(data, hashmap, restore_id)
