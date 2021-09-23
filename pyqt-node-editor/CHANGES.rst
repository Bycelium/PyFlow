Changelog (PyNodeEditor)
========================

0.9.6
-----

- QDMGraphicsEdgeDirect and QDMGraphicsEdgeBezier no longer derive from QDMGraphicsEdge
- QDMGraphicsEdge is now always used to represent graphics edge, and internaly got stored an instance of GraphicsEdgePathBase
- logic of calculating Direct and Bezier edges has moved to node_graphics_edge_path.py file into respective classes GraphicsEdgePathDirect and GraphicsEdgePathBezier
- possibility for NodeEditorWidget to override QDMGraphicsView class by setting `GraphicsView_class` class variable

0.9.5
-----

- fixed panning issue when drag edge caused by DragEdge being selectable edge

0.9.4
-----

- improvements to selection and edges

0.9.3
-----

- improved deserialization even with selections now

0.9.2
-----

- First polished and tested version of the library
- After 54 tutorials: https://www.blenderfreak.com/tutorials/node-editor-tutorial-series/