# -*- coding: utf-8 -*-
"""
A module containing the Edge Dragging functionality
"""
from nodeeditor.node_graphics_socket import QDMGraphicsSocket
from nodeeditor.node_edge import EDGE_TYPE_DEFAULT
from nodeeditor.utils import dumpException


DEBUG = False


class EdgeDragging:
    def __init__(self, grView:'QGraphicsView'):
        self.grView = grView
        # initializing these variable to know we're using them in this class...
        self.drag_edge = None
        self.drag_start_socket = None

    def getEdgeClass(self):
        """Helper function to get the Edge class. Using what Scene class provides"""
        return self.grView.grScene.scene.getEdgeClass()

    def updateDestination(self, x: float, y: float):
        """
        Update the end point of our dragging edge

        :param x: new X scene position
        :param y: new Y scene position
        """
        # according to sentry: 'NoneType' object has no attribute 'grEdge'
        if self.drag_edge is not None and self.drag_edge.grEdge is not None:
            self.drag_edge.grEdge.setDestination(x, y)
            self.drag_edge.grEdge.update()
        else:
            print(">>> Want to update self.drag_edge grEdge, but it's None!!!")


    def edgeDragStart(self, item:'QGraphicsItem'):
        """Code handling the start of a dragging an `Edge` operation"""
        try:
            if DEBUG: print('View::edgeDragStart ~ Start dragging edge')
            if DEBUG: print('View::edgeDragStart ~   assign Start Socket to:', item.socket)
            self.drag_start_socket = item.socket
            self.drag_edge = self.getEdgeClass()(item.socket.node.scene, item.socket, None, EDGE_TYPE_DEFAULT)
            self.drag_edge.grEdge.makeUnselectable()
            if DEBUG: print('View::edgeDragStart ~   dragEdge:', self.drag_edge)
        except Exception as e: dumpException(e)


    def edgeDragEnd(self, item:'QGraphicsItem'):
        """Code handling the end of the dragging an `Edge` operation. If this code returns True then skip the
        rest of the mouse event processing. Can be called with ``None`` to cancel the edge dragging mode

        :param item: Item in the `Graphics Scene` where we ended dragging an `Edge`
        :type item: ``QGraphicsItem``
        """

        # early out - clicked on something else than Socket
        if not isinstance(item, QDMGraphicsSocket):
            self.grView.resetMode()
            if DEBUG: print('View::edgeDragEnd ~ End dragging edge early')
            self.drag_edge.remove(silent=True)      # don't notify sockets about removing drag_edge
            self.drag_edge = None


        # clicked on socket
        if isinstance(item, QDMGraphicsSocket):

            # check if edge would be valid
            if not self.drag_edge.validateEdge(self.drag_start_socket, item.socket):
                print("NOT VALID EDGE")
                return False

            # regular processing of drag edge
            self.grView.resetMode()

            if DEBUG: print('View::edgeDragEnd ~ End dragging edge')
            self.drag_edge.remove(silent=True)      # don't notify sockets about removing drag_edge
            self.drag_edge = None

            try:
                if item.socket != self.drag_start_socket:
                    # if we released dragging on a socket (other then the beginning socket)

                    ## First remove old edges / send notifications
                    for socket in (item.socket, self.drag_start_socket):
                        if not socket.is_multi_edges:
                            if socket.is_input:
                                # print("removing SILENTLY edges from input socket (is_input and !is_multi_edges) [DragStart]:", item.socket.edges)
                                socket.removeAllEdges(silent=True)
                            else:
                                socket.removeAllEdges(silent=False)


                    ## Create new Edge
                    new_edge = self.getEdgeClass()(item.socket.node.scene, self.drag_start_socket, item.socket, edge_type=EDGE_TYPE_DEFAULT)
                    if DEBUG: print("View::edgeDragEnd ~  created new edge:", new_edge, "connecting", new_edge.start_socket, "<-->", new_edge.end_socket)

                    ## Send notifications for the new edge
                    for socket in [self.drag_start_socket, item.socket]:
                        # @TODO: Add possibility (ie when an input edge was replaced) to be silent and don't trigger change
                        socket.node.onEdgeConnectionChanged(new_edge)
                        if socket.is_input: socket.node.onInputChanged(socket)

                    self.grView.grScene.scene.history.storeHistory("Created new edge by dragging", setModified=True)
                    return True
            except Exception as e: dumpException(e)


        if DEBUG: print('View::edgeDragEnd ~ everything done.')
        return False

