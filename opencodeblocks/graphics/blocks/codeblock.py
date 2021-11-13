# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the base OCB Code Block. """

from typing import Optional

from PyQt5.QtCore import Qt, QByteArray, QPointF
from PyQt5.QtGui import QPainter, QPainterPath, QPixmap
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QWidget, QGraphicsProxyWidget, QLabel, \
    QGraphicsSceneMouseEvent, QApplication

from opencodeblocks.graphics.blocks.block import OCBBlock
from opencodeblocks.graphics.pyeditor import PythonEditor

class OCBCodeBlock(OCBBlock):

    """ 
    Code Block

    Features an area to edit code as well as a panel to display the output.

    """

    def __init__(self, **kwargs):
        """
        Note that self.output_panel_height < self.height,
        because the output panel is part of the display.
        Moreover, the following is always true:
        output_panel_height + source_panel_height + edge_size*2 + title_height == height
        """
        super().__init__(block_type='code', **kwargs)


        self.output_panel_height = 100
        self._min_output_panel_height = 20
        self._min_source_editor_height = 20

        assert self.height - self.output_panel_height \
         - self.title_height - self.edge_size*2 > 0

        self.source_editor = self.init_source_editor()
        self.display = self.init_display()
        self.stdout = ""
        self.image = ""

        self.resizing_source_code = False

        self.update_all() # Set the geometry of display and source_editor

    def init_source_editor(self):
        """ Initialize the python source code editor. """
        source_editor_graphics = QGraphicsProxyWidget(self)
        source_editor = PythonEditor(self)
        source_editor_graphics.setWidget(source_editor)
        source_editor_graphics.setZValue(-1)
        return source_editor_graphics

    def _editor_widget_height(self):
        return self.height - self.title_height - 2*self.edge_size \
                    - self.output_panel_height

    def update_all(self):
        """ Update the code block parts. """
        if hasattr(self, 'source_editor'):
            editor_widget = self.source_editor.widget()
            editor_widget.setGeometry(
                int(self.edge_size),
                int(self.edge_size + self.title_height),
                int(self._width - 2*self.edge_size),
                int(self._editor_widget_height())
            )
            display_widget = self.display.widget()
            display_widget.setGeometry(
                int(self.edge_size),
                int(self.height - self.output_panel_height - self.edge_size),
                int(self.width - 2*self.edge_size),
                int(self.output_panel_height)
            )
        super().update_all()

    @property
    def source(self) -> str:
        """ Source code. """
        return self._source
    @source.setter
    def source(self, value:str):
        self._source = value
        if hasattr(self, 'source_editor'):
            editor_widget = self.source_editor.widget()
            editor_widget.setText(self._source)

    @property
    def stdout(self) -> str:
        """ Code output, without errors """
        return self._stdout
    @stdout.setter
    def stdout(self, value:str):
        self._stdout = value
        if hasattr(self, 'source_editor'):
            # If there is a text output, erase the image output and display the text output
            self.image = ""
            editor_widget = self.display.widget()
            editor_widget.setText(self._stdout)

    @property
    def image(self) -> str:
        """ Code output. """
        return self._image
    @image.setter
    def image(self, value:str):
        self._image = value
        if hasattr(self, 'source_editor') and self.image != "":
            # If there is an image output, erase the text output and display the image output
            editor_widget = self.display.widget()
            editor_widget.setText("")
            qlabel = editor_widget
            ba = QByteArray.fromBase64(str.encode(self.image))
            pixmap = QPixmap()
            pixmap.loadFromData(ba)
            qlabel.setPixmap(pixmap)

    @source.setter
    def source(self, value:str):
        self._source = value
        if hasattr(self, 'source_editor'):
            editor_widget = self.source_editor.widget()
            editor_widget.setText(self._source)

    def paint(self, painter: QPainter,
            option: QStyleOptionGraphicsItem, #pylint:disable=unused-argument
            widget: Optional[QWidget]=None): #pylint:disable=unused-argument
        """ Paint the code output panel """
        super().paint(painter, option, widget)
        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.height,
            self.edge_size, self.edge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_title.simplified())


    def _is_in_code_output_resize_area(self, pos:QPointF):
        """ Return True if the given position is in the block resize_area. """
        source_editor_start = self.height - self.output_panel_height - self.edge_size

        return self.width - 2 * self.edge_size < pos.x() and \
             source_editor_start - self.edge_size < pos.y() < source_editor_start + self.edge_size
    
    def hoverMoveEvent(self, event):
        """ Triggered when hovering over a block """
        pos = event.pos()
        if self._is_in_resize_area(pos) or self._is_in_code_output_resize_area(pos):
            if not self.resizing_hover:
                self.resizing_hover = True
                QApplication.setOverrideCursor(Qt.CursorShape.SizeFDiagCursor)
        elif self.resizing_hover:
            self.resizing_hover = False
            QApplication.restoreOverrideCursor()
        # Don't call super() because this might override the cursor
    def hoverLeaveEvent(self, event):
        """ Triggered when the mouse stops hovering over a block """
        if self.resizing_hover:
            self.resizing_hover = False
            QApplication.restoreOverrideCursor()
        # Don't call super() because this might override the cursor

    def mousePressEvent(self, event:QGraphicsSceneMouseEvent):
        """ OCBBlock reaction to a mousePressEvent. """
        pos = event.pos()
        resizing_source_code = self._is_in_code_output_resize_area(pos)
        if (self._is_in_resize_area(pos) or resizing_source_code) and \
                event.buttons() == Qt.MouseButton.LeftButton:
            self.resize_start = pos
            self.resizing = True
            self.resizing_source_code = resizing_source_code
            QApplication.setOverrideCursor(Qt.CursorShape.SizeFDiagCursor)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event:QGraphicsSceneMouseEvent):
        """ OCBBlock reaction to a mouseReleaseEvent. """
        if self.resizing:
            self.scene().history.checkpoint("Resized block", set_modified=True)
        self.resizing = False
        self.resizing_source_code = False
        QApplication.restoreOverrideCursor()
        if self.moved:
            self.moved = False
            self.scene().history.checkpoint("Moved block", set_modified=True)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event:QGraphicsSceneMouseEvent):
        """ 
        We override the default resizing behavior as the code part and the display part of the block
        block can be resized. 
        """
        if self.resizing:
            delta = event.pos() - self.resize_start
            self.width = max(self.width + delta.x(), self._min_width)

            height_delta = max(delta.y(),
                # List of all the quantities that must remain negative.
                # Mainly: min_height - height must be negative for all elements
                self._min_output_panel_height - self.output_panel_height,
                self._min_height - self.height,
                self._min_source_editor_height - self._editor_widget_height()
            )

            self.height += height_delta
            if not self.resizing_source_code:
                self.output_panel_height += height_delta

            self.resize_start = event.pos()
            self.title_graphics.setTextWidth(self.width - 2 * self.edge_size)
            self.update()
        else:
            super().mouseMoveEvent(event)
            self.moved = True

    def init_display(self):
        """ Initialize the output display widget: QLabel """
        display_graphics = QGraphicsProxyWidget(self)
        display = QLabel()
        display.setText("")
        display_graphics.setWidget(display)
        display_graphics.setZValue(-1)
        return display_graphics
