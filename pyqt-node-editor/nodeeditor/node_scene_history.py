# -*- coding: utf-8 -*-
"""
A module containing all code for working with History (Undo/Redo)
"""
from nodeeditor.utils import dumpException

DEBUG = False
DEBUG_SELECTION = False


class SceneHistory():
    """Class contains all the code for undo/redo operations"""
    def __init__(self, scene: 'Scene'):
        """
        :param scene: Reference to the :class:`~nodeeditor.node_scene.Scene`
        :type scene: :class:`~nodeeditor.node_scene.Scene`

        :Instance Attributes:

        - **scene** - reference to the :class:`~nodeeditor.node_scene.Scene`
        - **history_limit** - number of history steps that can be stored
        """
        self.scene = scene

        self.clear()
        self.history_limit = 32

        self.undo_selection_has_changed = False

        # listeners
        self._history_modified_listeners = []
        self._history_stored_listeners = []
        self._history_restored_listeners = []

    def clear(self):
        """Reset the history stack"""
        self.history_stack = []
        self.history_current_step = -1

    def storeInitialHistoryStamp(self):
        """Helper function usually used when new or open file requested"""
        self.storeHistory("Initial History Stamp")

    def addHistoryModifiedListener(self, callback: 'function'):
        """
        Register callback for `HistoryModified` event

        :param callback: callback function
        """
        self._history_modified_listeners.append(callback)

    def addHistoryStoredListener(self, callback: 'function'):
        """
        Register callback for `HistoryStored` event

        :param callback: callback function
        """
        self._history_stored_listeners.append(callback)

    def addHistoryRestoredListener(self, callback: 'function'):
        """
        Register callback for `HistoryRestored` event

        :param callback: callback function
        """
        self._history_restored_listeners.append(callback)

    def canUndo(self) -> bool:
        """Return ``True`` if Undo is available for current `History Stack`

        :rtype: ``bool``
        """
        return self.history_current_step > 0

    def canRedo(self) -> bool:
        """
        Return ``True`` if Redo is available for current `History Stack`

        :rtype: ``bool``
        """
        return self.history_current_step + 1 < len(self.history_stack)

    def undo(self):
        """Undo operation"""
        if DEBUG: print("UNDO")

        if self.canUndo():
            self.history_current_step -= 1
            self.restoreHistory()
            self.scene.has_been_modified = True

    def redo(self):
        """Redo operation"""
        if DEBUG: print("REDO")
        if self.canRedo():
            self.history_current_step += 1
            self.restoreHistory()
            self.scene.has_been_modified = True


    def restoreHistory(self):
        """
        Restore `History Stamp` from `History stack`.

        Triggers:

        - `History Modified` event
        - `History Restored` event
        """
        if DEBUG: print("Restoring history",
                        ".... current_step: @%d" % self.history_current_step,
                        "(%d)" % len(self.history_stack))
        self.restoreHistoryStamp(self.history_stack[self.history_current_step])
        for callback in self._history_modified_listeners: callback()
        for callback in self._history_restored_listeners: callback()


    def storeHistory(self, desc: str, setModified: bool=False):
        """
        Store History Stamp into History Stack

        :param desc: Description of current History Stamp
        :type desc: ``str``
        :param setModified: if ``True`` marks :class:`~nodeeditor.node_scene.Scene` with `has_been_modified`
        :type setModified: ``bool``

        Triggers:

        - `History Modified`
        - `History Stored`
        """
        if setModified:
            self.scene.has_been_modified = True

        if DEBUG: print("Storing history", '"%s"' % desc,
                        ".... current_step: @%d" % self.history_current_step,
                        "(%d)" % len(self.history_stack))

        # if the pointer (history_current_step) is not at the end of history_stack
        if self.history_current_step+1 < len(self.history_stack):
            self.history_stack = self.history_stack[0:self.history_current_step+1]

        # history is outside of the limits
        if self.history_current_step+1 >= self.history_limit:
            self.history_stack = self.history_stack[1:]
            self.history_current_step -= 1

        hs = self.createHistoryStamp(desc)

        self.history_stack.append(hs)
        self.history_current_step += 1
        if DEBUG: print("  -- setting step to:", self.history_current_step)

        # always trigger history modified (for i.e. updateEditMenu)
        for callback in self._history_modified_listeners: callback()
        for callback in self._history_stored_listeners: callback()


    def captureCurrentSelection(self) -> dict:
        """
        Create dictionary with a list of selected nodes and a list of selected edges
        :return: ``dict`` 'nodes' - list of selected nodes, 'edges' - list of selected edges
        :rtype: ``dict``
        """
        sel_obj = {
            'nodes': [],
            'edges': [],
        }
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'): sel_obj['nodes'].append(item.node.id)
            elif hasattr(item, 'edge'): sel_obj['edges'].append(item.edge.id)
        return sel_obj

    def createHistoryStamp(self, desc: str) -> dict:
        """
        Create History Stamp. Internally serialize whole scene and the current selection

        :param desc: Descriptive label for the History Stamp
        :return: History stamp serializing state of `Scene` and current selection
        :rtype: ``dict``
        """
        history_stamp = {
            'desc': desc,
            'snapshot': self.scene.serialize(),
            'selection': self.captureCurrentSelection(),
        }

        return history_stamp

    def restoreHistoryStamp(self, history_stamp: dict):
        """
        Restore History Stamp to current `Scene` with selection of items included

        :param history_stamp: History Stamp to restore
        :type history_stamp: ``dict``
        """
        if DEBUG: print("RHS: ", history_stamp['desc'])

        try:
            self.undo_selection_has_changed = False
            previous_selection = self.captureCurrentSelection()
            if DEBUG_SELECTION: print("selected nodes before restore:", previous_selection['nodes'])

            self.scene.deserialize(history_stamp['snapshot'])

            # restore selection

            # first clear all selection on edges
            for edge in self.scene.edges: edge.grEdge.setSelected(False)
            # now restore selected edges from history_stamp
            for edge_id in history_stamp['selection']['edges']:
                for edge in self.scene.edges:
                    if edge.id == edge_id:
                        edge.grEdge.setSelected(True)
                        break

            # first clear all selection on nodes
            for node in self.scene.nodes: node.grNode.setSelected(False)
            # now restore selected nodes from history_stamp
            for node_id in history_stamp['selection']['nodes']:
                for node in self.scene.nodes:
                    if node.id == node_id:
                        node.grNode.setSelected(True)
                        break

            current_selection = self.captureCurrentSelection()
            if DEBUG_SELECTION: print("selected nodes after restore:", current_selection['nodes'])

            # reset the last_selected_items - since we're comparing change to the last_selected state
            self.scene._last_selected_items = self.scene.getSelectedItems()

            # if the selection of nodes differ before and after restoration, set flag
            if current_selection['nodes'] != previous_selection['nodes'] or current_selection['edges'] != previous_selection['edges']:
                if DEBUG_SELECTION: print("\nSCENE: Selection has changed")
                self.undo_selection_has_changed = True

        except Exception as e: dumpException(e)