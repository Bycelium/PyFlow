# -*- coding: utf-8 -*-
"""
A module containing the Edge Snapping functions which are used in :class:`~nodeeditor.node_graphics_view.QDMGraphicsView` class.
"""


from qtpy.QtCore import QPointF, QRectF
from nodeeditor.node_graphics_socket import QDMGraphicsSocket


class EdgeSnapping():
    def __init__(self, grView: 'QGraphicsView', snapping_radius: float = 24):
        self.grView = grView
        self.grScene = self.grView.grScene
        self.edge_snapping_radius = snapping_radius

    def getSnappedSocketItem(self, event: 'QMouseEvent') -> 'QDMGraphicsSocket':
        """Returns :class:`~nodeeditor.node_graphics_socket.QDMGraphicsSocket` which we should snap to"""
        scenepos = self.grView.mapToScene(event.pos())
        grSocket, pos = self.getSnappedToSocketPosition(scenepos)
        return grSocket

    def getSnappedToSocketPosition(self, scenepos: QPointF) -> ('QDMGraphicsSocket', QPointF):
        """
        Returns grSocket and Scene position to nearest Socket or original position if no nearby Socket found

        :param scenepos: From which point should I snap?
        :type scenepos: ``QPointF``
        :return: grSocket and Scene postion to nearest socket
        """
        scanrect = QRectF(
            scenepos.x() - self.edge_snapping_radius, scenepos.y() - self.edge_snapping_radius,
            self.edge_snapping_radius * 2, self.edge_snapping_radius * 2
        )
        items = self.grScene.items(scanrect)
        items = list(filter(lambda x: isinstance(x, QDMGraphicsSocket), items))

        if len(items) == 0:
            return None, scenepos

        selected_item = items[0]
        if len(items) > 1:
            # calculate the nearest socket
            nearest = 10000000000
            for grsock in items:
                grsock_scenepos = grsock.socket.node.getSocketScenePosition(grsock.socket)
                qpdist = QPointF(*grsock_scenepos) - scenepos
                dist = qpdist.x() * qpdist.x() + qpdist.y() * qpdist.y()
                if dist < nearest:
                    nearest, selected_item = dist, grsock

        selected_item.isHighlighted = True

        calcpos = selected_item.socket.node.getSocketScenePosition(selected_item.socket)

        return selected_item, QPointF(*calcpos)