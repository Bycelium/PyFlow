# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module to create and manage multi-threading workers """

import asyncio
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""

    stdout = pyqtSignal(str)
    image = pyqtSignal(str)
    finished = pyqtSignal()
    finished_block = pyqtSignal()
    error = pyqtSignal()


class Worker(QRunnable):
    """Worker thread."""

    def __init__(self, kernel, code):
        """Initialize the worker object."""
        super().__init__()

        self.kernel = kernel
        self.code = code
        self.signals = WorkerSignals()

    async def run_code(self):
        """Run the code in the block."""
        # Execute the code
        self.kernel.client.execute(self.code)
        done = False
        # While the kernel sends messages
        while done is False:
            # Save kernel message and send it to the GUI
            output, output_type, done = self.kernel.update_output()
            if done is False:
                if output_type == "text":
                    self.signals.stdout.emit(output)
                elif output_type == "image":
                    self.signals.image.emit(output)
                elif output_type == "error":
                    self.signals.error.emit()
                    self.signals.stdout.emit(output)
        self.signals.finished.emit()

    def run(self):
        """Execute the run_code method asynchronously."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_code())
        loop.close()
