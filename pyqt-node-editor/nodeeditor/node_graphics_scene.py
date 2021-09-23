# -*- coding: utf-8 -*-
"""
A module containing Graphic representation of :class:`~nodeeditor.node_scene.Scene`
"""
import math
from qtpy.QtWidgets import QGraphicsScene, QWidget
from qtpy.QtCore import Signal, QRect, QLine, Qt
from qtpy.QtGui import QColor, QPen, QFont, QPainter
from nodeeditor.utils import dumpException
from nodeeditor.node_graphics_view import STATE_STRING, DEBUG_STATE


class QDMGraphicsScene(QGraphicsScene):
    """Class representing Graphic of :class:`~nodeeditor.node_scene.Scene`"""
    #: pyqtSignal emitted when some item is selected in the `Scene`
    itemSelected = Signal()
    #: pyqtSignal emitted when items are deselected in the `Scene`
    itemsDeselected = Signal()

    def __init__(self, scene: 'Scene', parent: QWidget=None):
        """
        :param scene: reference to the :class:`~nodeeditor.node_scene.Scene`
        :type scene: :class:`~nodeeditor.node_scene.Scene`
        :param parent: parent widget
        :type parent: QWidget
        """
        super().__init__(parent)

        self.scene = scene

        # There is an issue when reconnecting edges -> mouseMove and trying to delete/remove them
        # the edges stayed in the scene in Qt, however python side was deleted
        # this caused a lot of troubles...
        #
        # I've spend months to find this sh*t!!
        #
        # https://bugreports.qt.io/browse/QTBUG-18021
        # https://bugreports.qt.io/browse/QTBUG-50691
        # Affected versions: 4.7.1, 4.7.2, 4.8.0, 5.5.1, 5.7.0 - LOL!
        self.setItemIndexMethod(QGraphicsScene.NoIndex)

        # settings
        self.gridSize = 20
        self.gridSquares = 5

        self.initAssets()
        self.setBackgroundBrush(self._color_background)

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._color_background = QColor("#393939")
        self._color_light = QColor("#2f2f2f")
        self._color_dark = QColor("#292929")
        self._color_state = QColor("#ccc")

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        self._pen_state = QPen(self._color_state)
        self._font_state = QFont("Ubuntu", 16)


    # the drag events won't be allowed until dragMoveEvent is overriden
    def dragMoveEvent(self, event):
        """Overriden Qt's dragMoveEvent to enable Qt's Drag Events"""
        pass

    def setGrScene(self, width: int, height: int):
        """Set `width` and `height` of the `Graphics Scene`"""
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter:QPainter, rect:QRect):
        """Draw background scene grid"""
        super().drawBackground(painter, rect)

        # here we create our grid
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.gridSize)
        first_top = top - (top % self.gridSize)

        # compute all lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.gridSize):
            if (x % (self.gridSize*self.gridSquares) != 0): lines_light.append(QLine(x, top, x, bottom))
            else: lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.gridSize):
            if (y % (self.gridSize*self.gridSquares) != 0): lines_light.append(QLine(left, y, right, y))
            else: lines_dark.append(QLine(left, y, right, y))


        # draw the lines
        painter.setPen(self._pen_light)
        try: painter.drawLines(*lines_light)                    # supporting PyQt5
        except TypeError: painter.drawLines(lines_light)        # supporting PySide2

        painter.setPen(self._pen_dark)
        try: painter.drawLines(*lines_dark)                     # supporting PyQt5
        except TypeError: painter.drawLines(lines_dark)         # supporting PySide2

        if DEBUG_STATE:
            try:
                painter.setFont(self._font_state)
                painter.setPen(self._pen_state)
                painter.setRenderHint(QPainter.TextAntialiasing)
                offset = 14
                rect_state = QRect(rect.x()+offset, rect.y()+offset, rect.width()-2*offset, rect.height()-2*offset)
                painter.drawText(rect_state, Qt.AlignRight | Qt.AlignTop, STATE_STRING[self.views()[0].mode].upper())
            except: dumpException()