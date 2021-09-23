# -*- coding: utf-8 -*-
"""
A module containing NodeEditor's class for representing Socket and Socket Position Constants.
"""
from collections import OrderedDict
from nodeeditor.node_serializable import Serializable
from nodeeditor.node_graphics_socket import QDMGraphicsSocket


LEFT_TOP = 1        #:
LEFT_CENTER =2      #:
LEFT_BOTTOM = 3     #:
RIGHT_TOP = 4       #:
RIGHT_CENTER = 5    #:
RIGHT_BOTTOM = 6    #:


DEBUG = False
DEBUG_REMOVE_WARNINGS = False


class Socket(Serializable):
    Socket_GR_Class = QDMGraphicsSocket

    """Class representing Socket."""

    def __init__(self, node: 'Node', index: int=0, position: int=LEFT_TOP, socket_type: int=1, multi_edges: bool=True,
                 count_on_this_node_side: int=1, is_input: bool=False):
        """
        :param node: reference to the :class:`~nodeeditor.node_node.Node` containing this `Socket`
        :type node: :class:`~nodeeditor.node_node.Node`
        :param index: Current index of this socket in the position
        :type index: ``int``
        :param position: Socket position. See :ref:`socket-position-constants`
        :param socket_type: Constant defining type(color) of this socket
        :param multi_edges: Can this socket have multiple `Edges` connected?
        :type multi_edges: ``bool``
        :param count_on_this_node_side: number of total sockets on this position
        :type count_on_this_node_side: ``int``
        :param is_input: Is this an input `Socket`?
        :type is_input: ``bool``

        :Instance Attributes:

            - **node** - reference to the :class:`~nodeeditor.node_node.Node` containing this `Socket`
            - **edges** - list of `Edges` connected to this `Socket`
            - **grSocket** - reference to the :class:`~nodeeditor.node_graphics_socket.QDMGraphicsSocket`
            - **position** - Socket position. See :ref:`socket-position-constants`
            - **index** - Current index of this socket in the position
            - **socket_type** - Constant defining type(color) of this socket
            - **count_on_this_node_side** - number of sockets on this position
            - **is_multi_edges** - ``True`` if `Socket` can contain multiple `Edges`
            - **is_input** - ``True`` if this socket serves for Input
            - **is_output** - ``True`` if this socket serves for Output
        """
        super().__init__()

        self.node = node
        self.position = position
        self.index = index
        self.socket_type = socket_type
        self.count_on_this_node_side = count_on_this_node_side
        self.is_multi_edges = multi_edges
        self.is_input = is_input
        self.is_output = not self.is_input


        if DEBUG: print("Socket -- creating with", self.index, self.position, "for nodeeditor", self.node)


        self.grSocket = self.__class__.Socket_GR_Class(self)

        self.setSocketPosition()

        self.edges = []

    def __str__(self):
        return "<Socket #%d %s %s..%s>" % (
            self.index, "ME" if self.is_multi_edges else "SE", hex(id(self))[2:5], hex(id(self))[-3:]
        )

    def delete(self):
        """Delete this `Socket` from graphics scene for sure"""
        self.grSocket.setParentItem(None)
        self.node.scene.grScene.removeItem(self.grSocket)
        del self.grSocket

    def changeSocketType(self, new_socket_type: int) -> bool:
        """
        Change the Socket Type

        :param new_socket_type: new socket type
        :type new_socket_type: ``int``
        :return: Returns ``True`` if the socket type was actually changed
        :rtype: ``bool``
        """
        if self.socket_type != new_socket_type:
            self.socket_type = new_socket_type
            self.grSocket.changeSocketType()
            return True
        return False

    def setSocketPosition(self):
        """Helper function to set `Graphics Socket` position. Exact socket position is calculated
        inside :class:`~nodeeditor.node_node.Node`."""
        self.grSocket.setPos(*self.node.getSocketPosition(self.index, self.position, self.count_on_this_node_side))

    def getSocketPosition(self):
        """
        :return: Returns this `Socket` position according to the implementation stored in
            :class:`~nodeeditor.node_node.Node`
        :rtype: ``x, y`` position
        """
        if DEBUG: print("  GSP: ", self.index, self.position, "nodeeditor:", self.node)
        res = self.node.getSocketPosition(self.index, self.position, self.count_on_this_node_side)
        if DEBUG: print("  res", res)
        return res


    def hasAnyEdge(self) -> bool:
        """
        Returns ``True`` if any :class:`~nodeeditor.node_edge.Edge` is connected to this socket

        :return: ``True`` if any :class:`~nodeeditor.node_edge.Edge` is connected to this socket
        :rtype: ``bool``
        """
        return len(self.edges) > 0

    def isConnected(self, edge: 'Edge') -> bool:
        """
        Returns ``True`` if :class:`~nodeeditor.node_edge.Edge` is connected to this `Socket`

        :param edge: :class:`~nodeeditor.node_edge.Edge` to check if it is connected to this `Socket`
        :type edge: :class:`~nodeeditor.node_edge.Edge`
        :return: ``True`` if `Edge` is connected to this socket
        :rtype: ``bool``
        """
        return edge in self.edges

    def addEdge(self, edge: 'Edge'):
        """
        Append an Edge to the list of connected Edges

        :param edge: :class:`~nodeeditor.node_edge.Edge` to connect to this `Socket`
        :type edge: :class:`~nodeeditor.node_edge.Edge`
        """
        self.edges.append(edge)

    def removeEdge(self, edge: 'Edge'):
        """
        Disconnect passed :class:`~nodeeditor.node_edge.Edge` from this `Socket`
        :param edge: :class:`~nodeeditor.node_edge.Edge` to disconnect
        :type edge: :class:`~nodeeditor.node_edge.Edge`
        """
        if edge in self.edges: self.edges.remove(edge)
        else:
            if DEBUG_REMOVE_WARNINGS:
                print("!W:", "Socket::removeEdge", "wanna remove edge", edge,
                      "from self.edges but it's not in the list!")

    def removeAllEdges(self, silent: bool=False):
        """Disconnect all `Edges` from this `Socket`"""
        while self.edges:
            edge = self.edges.pop(0)
            if silent:
                edge.remove(silent_for_socket=self)
            else:
                edge.remove()       # just remove all with notifications

    def determineMultiEdges(self, data: dict) -> bool:
        """
        Deserialization helper function. In our tutorials we created a new version of graph data format.
        This function is here to help solve the issue of opening older files in the newer format.
        If the 'multi_edges' param is missing in the dictionary, we determine if this `Socket`
        should support multiple `Edges`.

        :param data: `Socket` data in ``dict`` format for deserialization
        :type data: ``dict``
        :return: ``True`` if this `Socket` should support multi_edges
        """
        if 'multi_edges' in data:
            return data['multi_edges']
        else:
            # probably older version of file, make RIGHT socket multiedged by default
            return data['position'] in (RIGHT_BOTTOM, RIGHT_TOP)

    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('multi_edges', self.is_multi_edges),
            ('position', self.position),
            ('socket_type', self.socket_type),
        ])

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        if restore_id: self.id = data['id']
        self.is_multi_edges = self.determineMultiEdges(data)
        self.changeSocketType(data['socket_type'])
        hashmap[data['id']] = self
        return True