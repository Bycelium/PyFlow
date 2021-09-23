# -*- coding: utf-8 -*-
"""
A module containing the Edge Rerouting functionality
"""


DEBUG_REROUTING = True


class EdgeRerouting:
    def __init__(self, grView: 'QGraphicsView'):
        self.grView = grView
        self.start_socket = None        # store where we started re-routing the edges
        self.rerouting_edges = []       # edges representing the re-routing (dashed edges)
        self.is_rerouting = False       # are we currently re-routing?
        self.first_mb_release = False   # flag for detecting if we already clicked with the rerouting LMB release

    def print(self, *args):
        """Helper function to better control debug printing to console for this feature"""
        if DEBUG_REROUTING: print("REROUTING:", *args)

    def getEdgeClass(self):
        """Helper function to get the Edge class. Using what the Scene class provides"""
        return self.grView.grScene.scene.getEdgeClass()

    def getAffectedEdges(self) -> list:
        """
        Get a list of all edges connected to the `self.start_socket` where we started the re-routing

        :return: List of all edges affected by the rerouting started from this `self.start_socket` :class:`~nodeeditor.node_socket.Socket`
        :rtype: ``list``
        """
        if self.start_socket is None:
            return []       # no starting socket assigned, so no edges for us
        # return edges connected to the socket
        return self.start_socket.edges.copy()

    def setAffectedEdgesVisible(self, visibility: bool=True):
        """
        Show/Hide all edges connected to the `self.start_socket` where we started the re-routing

        :param visibility: ``True`` if all the affected :class:`~nodeeditor.node_edge.Edge` (s) should be shown or hidden
        :type visibility: ``bool``
        """
        for edge in self.getAffectedEdges():
            if visibility: edge.grEdge.show()
            else: edge.grEdge.hide()

    def resetRerouting(self):
        """Reset to default state. Init this feature internal variables"""
        self.is_rerouting = False
        self.start_socket = None
        self.first_mb_release = False
        # holding all rerouting edges should be empty at this point...
        # self.rerouting_edges = []

    def clearReroutingEdges(self):
        """Remove the helping dashed edges from the :class:`~nodeeditor.node_scene.Scene`"""
        self.print("clean called")
        while self.rerouting_edges != []:
            edge = self.rerouting_edges.pop()
            self.print("\twant to clean:", edge)
            edge.remove()

    def updateScenePos(self, x: float, y: float):
        """
        Update position of all the rerouting edges (dashed ones). Called from mouseMove event to update to new mouse position

        :param x: new X position
        :type x: ``float``
        :param y: new Y position
        :type y: ``float``
        """
        if self.is_rerouting:
            for edge in self.rerouting_edges:
                if edge and edge.grEdge:
                    edge.grEdge.setDestination(x, y)
                    edge.grEdge.update()

    def startRerouting(self, socket: 'Socket'):
        """
        Method to start the re-routing. Called from the grView's state machine.

        :param socket: :class:`~nodeeditor.node_socket.Socket` where we started the re-routing
        :type socket: :class:`~nodeeditor.node_socket.Socket`
        """
        self.print("startRerouting", socket)
        self.is_rerouting = True
        self.start_socket = socket

        self.print("numEdges:", len(self.getAffectedEdges()))
        self.setAffectedEdgesVisible(visibility=False)

        start_position = self.start_socket.node.getSocketScenePosition(self.start_socket)

        for edge in self.getAffectedEdges():
            other_socket = edge.getOtherSocket(self.start_socket)

            new_edge = self.getEdgeClass()(self.start_socket.node.scene, edge_type=edge.edge_type)
            new_edge.start_socket = other_socket
            new_edge.grEdge.setSource(*other_socket.node.getSocketScenePosition(other_socket))
            new_edge.grEdge.setDestination(*start_position)
            new_edge.grEdge.update()
            self.rerouting_edges.append(new_edge)


    def stopRerouting(self, target: 'Socket'=None):
        """
        Method for stopping the re-routing

        :param target: Target where we ended the rerouting (usually released mouse button). Provide ``Socket`` or ``None`` to cancel
        :type target: :class:`~nodeeditor.node_socket.Socket` or ``None``
        """
        self.print("stopRerouting on:", target, "no change" if target==self.start_socket else "")

        if self.start_socket is not None:
            # reset start socket highlight
            self.start_socket.grSocket.isHighlighted = False

        # collect all affected (node, edge) tuples in the meantime.. if necessary
        affected_nodes = []

        if target is None or target == self.start_socket:
            # canceling -> no change
            self.setAffectedEdgesVisible(visibility=True)

        else:
            # validate edges before doing anything else
            valid_edges, invalid_edges = self.getAffectedEdges(), []
            for edge in self.getAffectedEdges():
                start_sock = edge.getOtherSocket(self.start_socket)
                if not edge.validateEdge(start_sock, target):
                    # not valid edge
                    self.print("This edge rerouting is not valid!", edge)
                    invalid_edges.append(edge)

            # remove the invalidated edges from the list
            for invalid_edge in invalid_edges:
                valid_edges.remove(invalid_edge)

            # reconnect to new socket
            self.print("should reconnect from:", self.start_socket, "-->", target)

            self.setAffectedEdgesVisible(visibility=True)

            for edge in valid_edges:
                for node in [edge.start_socket.node, edge.end_socket.node]:
                    if node not in affected_nodes:
                        affected_nodes.append((node, edge))

                if target.is_input:
                    target.removeAllEdges(silent=True)

                if edge.end_socket == self.start_socket:
                    edge.end_socket = target
                else:
                    edge.start_socket = target

                edge.updatePositions()


        # hide rerouting edges
        self.clearReroutingEdges()

        # Send notifications for all affected nodes
        for affected_node, edge in affected_nodes:
            affected_node.onEdgeConnectionChanged(edge)
            if edge.start_socket in affected_node.inputs:
                affected_node.onInputChanged(edge.start_socket)
            if edge.end_socket in affected_node.inputs:
                affected_node.onInputChanged(edge.end_socket)

        # store history stamp
        self.start_socket.node.scene.history.storeHistory("Rerouted edges", setModified=True)

        # reset variables of this rerouting state
        self.resetRerouting()
