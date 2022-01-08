# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

""" Module for the handling a PythonEditor history. """

from typing import TYPE_CHECKING, Optional, OrderedDict, Tuple

from pyflow.core.history import History

if TYPE_CHECKING:
    from pyflow.core.pyeditor import PythonEditor


class EditorHistory(History):
    """
    Helper object to handle undo/redo operations on a PythonEditor.

    Args:
        editor: PythonEditor reference.
        max_stack: Maximum size of the history stack (number of available undo).

    """

    def __init__(self, editor: "PythonEditor", max_stack: int = 50):
        self.editor = editor
        self.is_writing = False
        super().__init__(max_stack)

    def start_sequence(self):
        """
        Start a new writing sequence if it was not already the case, and save the current state.
        """
        if not self.is_writing:
            self.is_writing = True
            self.checkpoint()

    def end_sequence(self):
        """
        End the writing sequence if it was not already the case.
        Do not save at this point because the writing parameters to be saved (cursor pos, etc) 
        are the one of the beginning of the next sequence.
        """
        self.is_writing = False

    def checkpoint(self):
        """
        Store a snapshot of the editor's text and parameters in the history stack 
        (only if the text has changed).
        """
        text: str = self.editor.text()
        old_data = self.restored_data()
        if old_data is not None and old_data["text"] == text:
            return

        cursor_pos: Tuple[int, int] = self.editor.getCursorPosition()
        scroll_pos: int = self.editor.verticalScrollBar().value()
        self.store(
            {
                "text": text,
                "cursor_pos": cursor_pos,
                "scroll_pos": scroll_pos,
            }
        )

    def restore(self):
        """
        Restore the editor's text and parameters 
        using the snapshot pointed by current in the history stack.
        """
        data: Optional[OrderedDict] = self.restored_data()

        if data is not None:
            self.editor.setText(data["text"])
            self.editor.setCursorPosition(*data["cursor_pos"])
            self.editor.verticalScrollBar().setValue(data["scroll_pos"])
