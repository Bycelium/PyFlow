import math
from qtpy.QtCore import QPointF
from qtpy.QtGui import QPainterPath


EDGE_CP_ROUNDNESS = 100     #: Bezier control point distance on the line
WEIGHT_SOURCE = 0.2         #: factor for square edge to change the midpoint between start and end socket


class GraphicsEdgePathBase:
    """Base Class for calculating the graphics path to draw for an graphics Edge"""

    def __init__(self, owner: 'QDMGraphicsEdge'):
        # keep the reference to owner GraphicsEdge class
        self.owner = owner

    def calcPath(self):
        """Calculate the Direct line connection

        :returns: ``QPainterPath`` of the graphics path to draw
        :rtype: ``QPainterPath`` or ``None``
        """
        return None


class GraphicsEdgePathDirect(GraphicsEdgePathBase):
    """Direct line connection Graphics Edge"""
    def calcPath(self) -> QPainterPath:
        """Calculate the Direct line connection

        :returns: ``QPainterPath`` of the direct line
        :rtype: ``QPainterPath``
        """
        path = QPainterPath(QPointF(self.owner.posSource[0], self.owner.posSource[1]))
        path.lineTo(self.owner.posDestination[0], self.owner.posDestination[1])
        return path


class GraphicsEdgePathBezier(GraphicsEdgePathBase):
    """Cubic line connection Graphics Edge"""
    def calcPath(self) -> QPainterPath:
        """Calculate the cubic Bezier line connection with 2 control points

        :returns: ``QPainterPath`` of the cubic Bezier line
        :rtype: ``QPainterPath``
        """
        s = self.owner.posSource
        d = self.owner.posDestination
        dist = (d[0] - s[0]) * 0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.owner.edge.start_socket is not None:
            ssin = self.owner.edge.start_socket.is_input
            ssout = self.owner.edge.start_socket.is_output

            if (s[0] > d[0] and ssout) or (s[0] < d[0] and ssin):
                cpx_d *= -1
                cpx_s *= -1

                cpy_d = (
                    (s[1] - d[1]) / math.fabs(
                        (s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001
                    )
                ) * EDGE_CP_ROUNDNESS
                cpy_s = (
                    (d[1] - s[1]) / math.fabs(
                        (d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001
                    )
                ) * EDGE_CP_ROUNDNESS

        path = QPainterPath(QPointF(self.owner.posSource[0], self.owner.posSource[1]))
        path.cubicTo( s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d, self.owner.posDestination[0], self.owner.posDestination[1])

        return path


class GraphicsEdgePathSquare(GraphicsEdgePathBase):
    """Square line connection Graphics Edge"""
    def __init__(self, *args, handle_weight=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.rand = None
        self.handle_weight = handle_weight

    def calcPath(self):
        """Calculate the square edge line connection

        :returns: ``QPainterPath`` of the edge square line
        :rtype: ``QPainterPath``
        """

        s = self.owner.posSource
        d = self.owner.posDestination

        mid_x = s[0] + ((d[0] - s[0]) * self.handle_weight)

        path = QPainterPath(QPointF(s[0], s[1]))
        path.lineTo(mid_x, s[1])
        path.lineTo(mid_x, d[1])
        path.lineTo(d[0], d[1])

        return path
