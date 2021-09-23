# -*- coding: utf-8 -*-
"""
A module containing the intersecting nodes functionality. If a node gets dragged and dropped on an existing edge
it will intersect that edge.
"""
from qtpy.QtWidgets import QGraphicsView
from qtpy.QtCore import QRectF
from nodeeditor.node_edge import Edge


class EdgeIntersect:

    def __init__(self, grView: "QGraphicsView"):
        self.grScene = grView.grScene
        self.grView = grView
        self.draggedNode = None
        self.hoveredList = []

    def enterState(self, node: "Node"):
        """
        Initialize when we enter the state

        :param node: :class:`~nodeeditor.node_node.Node` which we started to drag
        :type node: :class:`~nodeeditor.node_node.Node`
        """
        self.hoveredList = []
        self.draggedNode = node

    def leaveState(self, scene_pos_x: float, scene_pos_y: float):
        """
        Deinit when we leave this state

        :param scene_pos_x: scene position x
        :type scene_pos_x: `float`
        :param scene_pos_y: scene position y
        :type scene_pos_y: `float`
        """
        self.dropNode(self.draggedNode, scene_pos_x, scene_pos_y)
        self.draggedNode = None
        self.hoveredList = []

    def dropNode(self, node: "Node", scene_pos_x: float, scene_pos_y: float):
        """
        Code handling the dropping of a node on an existing edge.

        :param scene_pos_x: scene position x
        :type scene_pos_x: `float`
        :param scene_pos_y: scene position y
        :type scene_pos_y: `float`
        """

        node_box = self.hotZoneRect(node)

        # check if the node is dropped on an existing edge
        edge = self.intersect(node_box)
        if edge is None: return

        if self.isConnected(node): return

        # determine the order of start and end
        if edge.start_socket.is_output:
            socket_start = edge.start_socket
            socket_end = edge.end_socket
        else:
            socket_start = edge.end_socket
            socket_end = edge.start_socket

        # The new edges will have the same edge_type as the intersected edge
        edge_type = edge.edge_type
        edge.remove()
        self.grView.grScene.scene.history.storeHistory('Delete existing edge', setModified=True)

        new_node_socket_in = node.inputs[0]
        Edge(self.grScene.scene, socket_start, new_node_socket_in, edge_type=edge_type)
        new_node_socket_out = node.outputs[0]
        Edge(self.grScene.scene, new_node_socket_out, socket_end, edge_type=edge_type)

        self.grView.grScene.scene.history.storeHistory('Created new edges by dropping node', setModified=True)


    def hotZoneRect(self, node: 'Node') -> 'QRectF':
        """
        Returns A QRectF of creating a box around a node

        :param node: :class:`~nodeeditor.node_node.Node` for which we want to get `QRectF` describing its position and area
        :type node: :class:`~nodeeditor.node_node.Node`
        :return: `QRectF` describing node's position and area
        :rtype: `QRectF`
        """
        nodePos = node.grNode.scenePos()
        x = nodePos.x()
        y = nodePos.y()
        w = node.grNode.width
        h = node.grNode.height
        return QRectF(x, y, w, h)


    def update(self, scene_pos_x: float, scene_pos_y: float):
        """
        Updating during mouse move when grView is in this state

        :param scene_pos_x: scene position x
        :type scene_pos_x: `float`
        :param scene_pos_y: scene position y
        :type scene_pos_y: `float`
        """
        rect = self.hotZoneRect(self.draggedNode)
        grItems = self.grScene.items(rect)
        for grEdge in self.hoveredList: grEdge.hovered = False
        self.hoveredList = []
        for grItem in grItems:
            if hasattr(grItem, 'edge') and not self.draggedNode.hasConnectedEdge(grItem.edge):
                self.hoveredList.append(grItem)
                grItem.hovered = True

    def intersect(self, node_box: 'QRectF') -> 'Edge':
        """
        Checking for intersection of a rectangle (usually a `Node`) with edges in the scene

        :param node_box: `QRectF` for which we want find intersecting `Edges`
        :type node_box: `QRectF`
        :return: :class:`~nodeeditor.node_edge.Edge` or `None` if the node is being cut by an `Edge`
        :rtype: :class:`~nodeeditor.node_edge.Edge`
        """
        # returns the first edge that intersects with the dropped node, ignores the rest
        grItems = self.grScene.items(node_box)
        for grItem in grItems:
            if hasattr(grItem, 'edge') and not self.draggedNode.hasConnectedEdge(grItem.edge):
                return grItem.edge
        return None

    def isConnected(self, node: 'Node'):
        """
        Return ``True`` if node got any connections

        :param node: :class:`~nodeeditor.node_node.Node` which connections to check
        :type node: :class:`~nodeeditor.node_node.Node`
        :return:
        """
        # Nodes with only inputs or outputs are excluded
        if node.inputs == [] or node.outputs == []: return True

        # Check if the node has edges connected
        return node.getInput() or node.getOutputs()
