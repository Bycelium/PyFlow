
""" Module to create and manage ipython kernels """

import queue
from typing import Tuple
from jupyter_client.manager import start_new_kernel

from opencodeblocks.graphics.worker import Worker


class Kernel():

    """jupyter_client kernel used to execute code and return output"""

    def __init__(self):
        self.kernel_manager, self.client = start_new_kernel()
        self.execution_queue = []
        self.busy = False

    def message_to_output(self, message: dict) -> Tuple[str, str]:
        """
        Converts a message sent by the kernel into a relevant output

        Args:
            message: dict representing the a message sent by the kernel

        Return:
            single output found in the message in that order of priority:
                image > text data > text print > error > nothing
        """
        message_type = 'None'
        if 'data' in message:
            if 'image/png' in message['data']:
                message_type = 'image'
                # output an image (from plt.plot or plt.imshow)
                out = message['data']['image/png']
            else:
                message_type = 'text'
                # output data as str (for example if code="a=10\na")
                out = message['data']['text/plain']
        elif 'name' in message and message['name'] == "stdout":
            message_type = 'text'
            # output a print (print("Hello World"))
            out = message['text']
        elif 'traceback' in message:
            message_type = 'text'
            # output an error
            out = '\n'.join(message['traceback'])
        else:
            message_type = 'text'
            out = ''
        return out, message_type

    def run_block(self, block, code: str):
        """
        Runs code on a separate thread and sends the output to the block
        Also calls run_queue when finished

        Args:
            block: OCBCodeBlock to send the output to
            code: String representing a piece of Python code to execute
        """
        worker = Worker(self, code)
        worker.signals.stdout.connect(block.handle_stdout)
        worker.signals.image.connect(block.handle_image)
        worker.signals.finished.connect(self.run_queue)
        worker.signals.finished_block.connect(block.reset_after_run)
        block.source_editor.threadpool.start(worker)

    def run_queue(self):
        """ Runs the next code in the queue """
        self.busy = True
        if self.execution_queue == []:
            self.busy = False
            return None
        block, code = self.execution_queue.pop(0)
        self.run_block(block, code)

    def execute(self, code: str) -> str:
        """
        Executes code in the kernel and returns the output of the last message sent by the kernel

        Args:
            code: String representing a piece of Python code to execute

        Return:
            output from the last message sent by the kernel
        """
        _ = self.client.execute(code)
        done = False
        while not done:
            # Check for messages, break the loop when the kernel stops sending messages
            new_message, done = self.get_message()
            if not done:
                message = new_message
        return self.message_to_output(message)[0]

    def get_message(self) -> Tuple[str, bool]:
        """
        Get message in the jupyter kernel

        Args:
            code: String representing a piece of Python code to execute

        Return:
            Tuple of:
                - output from the last message sent by the kernel
                - boolean repesenting if the kernel as any other message to send.
        """
        done = False
        try:
            message = self.client.get_iopub_msg(timeout=1000)['content']
            if 'execution_state' in message and message['execution_state'] == 'idle':
                done = True
        except queue.Empty:
            message = None
            done = True
        return message, done

    def update_output(self) -> Tuple[str, str, bool]:
        """
        Returns the current output of the kernel

        Return:
            current output of the kernel; done: bool, True if the kernel has no message to send
        """
        message, done = self.get_message()
        out, output_type = self.message_to_output(message)
        return out, output_type, done

    def __del__(self):
        """
        Shuts down the kernel
        """
        self.kernel_manager.shutdown_kernel()
