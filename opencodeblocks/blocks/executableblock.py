""" Module for the executable block class """

from typing import List, OrderedDict

from networkx.algorithms.traversal.breadth_first_search import bfs_edges

from opencodeblocks.blocks.block import OCBBlock
from opencodeblocks.graphics.socket import OCBSocket

from opencodeblocks.graphics.kernel import get_main_kernel

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
        self.is_running = False

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
        """ Run the code in the block"""

        # Queue the code to execute
        code = self.source
        kernel = get_main_kernel()
        kernel.execution_queue.append((self, code))
        
        self.is_running = True

        if kernel.busy is False:
            kernel.run_queue()
        self.has_been_run = True

    def execution_finished(self):
        """
        Method called when the execution of the block is finished.
        Implement the behavior you want here.
        """
        self.is_running = False

    @staticmethod
    def _interrupt_execution():
        """ Interrupt an execution, reset the blocks in the queue """
        kernel = get_main_kernel()
        for block, _ in kernel.execution_queue:
            # Reset the blocks that have not been run
            block.execution_finished()
            block.has_been_run = False
        # Clear the queue
        kernel.execution_queue = []
        # Interrupt the kernel
        kernel.kernel_manager.interrupt_kernel()

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

    def run_left(self, in_run_right=False):
        """
        Run all of the block's dependencies and then run the block
        """

        if self.has_input():
            # Create the graph from the scene
            graph = self.scene().create_graph()
            # BFS through the input graph
            edges = bfs_edges(graph, self, reverse=True)
            # Run the blocks found except self
            blocks_to_run: List["OCBExecutableBlock"] = [v for _, v in edges]
            for block in blocks_to_run[::-1]:
                if not block.has_been_run:
                    block.run_code()
        
        if self.is_running: return
        self.run_code()

    def run_right(self):
        """Run all of the output blocks and all their dependencies"""

        # If no output, run left
        if not self.has_output():
            self.run_left(in_run_right=True)
            return

        # Same as run_left but instead of running the blocks, we'll use run_left
        graph = self.scene().create_graph()
        edges = bfs_edges(graph, self)
        blocks_to_run: List["OCBExecutableBlock"] = [
            self] + [v for _, v in edges]
        for block in blocks_to_run[::-1]:
            block.run_left(in_run_right=True)

    def reset_has_been_run(self):
        """ Called when the output is an error """
        self.has_been_run = False


    @property
    def source(self) -> str:
        """Source code"""
        raise NotImplementedError("source(self) should be overriden")

    @source.setter
    def source(self, value: str):
        raise NotImplementedError("source(self) should be overriden")


    def handle_stdout(self, value: str):
        """Handle the stdout signal"""
        pass

    def handle_image(self, image: str):
        """Handle the image signal"""
        pass

    def serialize(self):
        """Return a serialized version of this block"""
        base_dict = super().serialize()
        base_dict["source"] = self.source
        return base_dict

    def deserialize(
        self, data: OrderedDict, hashmap: dict = None, restore_id: bool = True
    ):
        """Restore a codeblock from it's serialized state"""
        for dataname in ("source"):
            if dataname in data:
                setattr(self, dataname, data[dataname])
        super().deserialize(data, hashmap, restore_id)
