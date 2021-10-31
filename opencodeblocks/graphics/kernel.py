import queue
from jupyter_client.manager import start_new_kernel


class Kernel():

    def __init__(self):
        self.kernel_manager, self.client = start_new_kernel()

    def execute(self, code):
        _ = self.client.execute(code)
        io_msg_content = []
        if 'execution_state' in io_msg_content and io_msg_content['execution_state'] == 'idle':
            return "no output"

        while True:
            temp = io_msg_content
            try:
                io_msg_content = self.client.get_iopub_msg(timeout=1000)[
                    'content']
                if 'execution_state' in io_msg_content and io_msg_content['execution_state'] == 'idle':
                    break
            except queue.Empty:
                break

        if 'data' in temp:
            if 'image/png' in temp['data']:
                out = temp['data']['image/png']
            else:
                out = temp['data']['text/plain']
        elif 'name' in temp and temp['name'] == "stdout":
            out = temp['text']
        elif 'traceback' in temp:
            out = '\n'.join(temp['traceback'])
        else:
            out = ''
        return out

    def __del__(self):
        self.kernel_manager.shutdown_kernel()
