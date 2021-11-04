
""" Module to create and manage ipython kernels """

import queue
from typing import Tuple
from jupyter_client.manager import start_new_kernel


class Kernel():

    def __init__(self):
        self.kernel_manager, self.client = start_new_kernel()

    def message_to_output(self, message: dict) -> Tuple[str, str]:
        """
        Converts a message sent by the kernel into a relevant output

        Args:
            message: dict representing the a message sent by the kernel

        Return:
            single output found in the message in that order of priority: image > text data > text print > error > nothing
            type: 'image' or 'text'
        """
        type = 'None'
        if 'data' in message:
            if 'image/png' in message['data']:
                type = 'image'
                # output an image (from plt.plot or plt.imshow)
                out = message['data']['image/png']
            else:
                type = 'text'
                # output data as str (for example if code="a=10\na")
                out = message['data']['text/plain']
        elif 'name' in message and message['name'] == "stdout":
            type = 'text'
            # output a print (print("Hello World"))
            out = message['text']
        elif 'traceback' in message:
            type = 'text'
            # output an error
            out = '\n'.join(message['traceback'])
        else:
            type = 'text'
            out = ''
        return out, type

    def execute(self, code: str) -> str:
        """
        Executes code in the kernel and returns the output of the last message sent by the kernel in return

        Args:
            code: str representing a piece of Python code to execute

        Return:
            output from the last message sent by the kernel in return
        """
        _ = self.client.execute(code)
        io_msg_content = {}
        if 'execution_state' in io_msg_content and io_msg_content['execution_state'] == 'idle':
            return "no output"

        while True:
            # Check for messages, break the loop when the kernel stops sending messages
            message = io_msg_content
            try:
                io_msg_content = self.client.get_iopub_msg(timeout=1000)[
                    'content']
                if 'execution_state' in io_msg_content and io_msg_content['execution_state'] == 'idle':
                    break
            except queue.Empty:
                break

        return self.message_to_output(message)[0]

    def update_output(self) -> Tuple[str, str, bool]:
        """
        Returns the current output of the kernel

        Return:
            current output of the kernel; done: bool, True if the kernel has no message to send
        """
        message = None
        done = False
        try:
            message = self.client.get_iopub_msg(timeout=1000)[
                'content']
            if 'execution_state' in message and message['execution_state'] == 'idle':
                done = True
        except queue.Empty:
            done = True

        out, type = self.message_to_output(message)

        return out, type, done

    def __del__(self):
        """
        Shuts down the kernel
        """
        self.kernel_manager.shutdown_kernel()
