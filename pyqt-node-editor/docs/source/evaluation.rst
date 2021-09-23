.. _evaluation:

Evaluation
==========

TL;DR: The evaluation system uses
:func:`~nodeeditor.node_node.Node.eval` and
:func:`~nodeeditor.node_node.Node.evalChildren`. ``eval()`` method is supposed to be overriden by your own
implementation. The evaluation logic uses Flags for marking the `Nodes` to be `Dirty` and/or `Invalid`.

Evaluation Functions
--------------------

There are 2 main methods used for evaluation:

- :func:`~nodeeditor.node_node.Node.eval`
- :func:`~nodeeditor.node_node.Node.evalChildren`

These functions are mutually exclusive. That means that ``evalChildren`` does **not** eval current `Node`,
but only children of the current `Node`.

By default the implementation of :func:`~nodeeditor.node_node.Node.eval` is "empty" and return 0. However
it seems logical, that eval (if successfull) resets the `Node` not to be `Dirty` nor `Invalid`.
This method is supposed to be overriden by your own implementation. As an example, you can check out
the repository's ``examples/example_calculator`` to have an inspiration how to setup the
`Node` evaluation on your own.

The evaluation takes advantage of `Node` flags described below.

:class:`~nodeeditor.node_node.Node` Flags
-----------------------------------------

Each :class:`~nodeeditor.node_node.Node` has 2 flags:

- ``Dirty``
- ``Invalid``

The `Invalid` flag has always higher priority. That means when the `Node` is `Invalid` it
doesn't matter if it is `Dirty` or not.

To mark a node `Dirty` or `Invalid` there are respective methods :func:`~nodeeditor.node_node.Node.markDirty`
and :func:`~nodeeditor.node_node.Node.markInvalid`. Both methods take `bool` parameter for the new state.
You can mark `Node` dirty by setting the parameter to ``True``. Also you can un-mark the state by passing
``False`` value.

For both flags there are 3 methods available:

- :func:`~nodeeditor.node_node.Node.markInvalid` - to mark only the `Node`
- :func:`~nodeeditor.node_node.Node.markChildrenInvalid` - to mark only the direct (first level) children of the `Node`
- :func:`~nodeeditor.node_node.Node.markDescendantsInvalid` - to mark it self and all descendant children of the `Node`

The same goes for the `Dirty` flag of course:

- :func:`~nodeeditor.node_node.Node.markDirty` - to mark only the `Node`
- :func:`~nodeeditor.node_node.Node.markChildrenDirty` - to mark only the direct (first level) children of the `Node`
- :func:`~nodeeditor.node_node.Node.markDescendantsDirty` - to mark it self and all descendant children of the `Node`

Descendants or Children are always connected to Output(s) of current `Node`.

When a node is marked `Dirty` or `Invalid` event methods
:func:`~nodeeditor.node_node.Node.onMarkedInvalid`
:func:`~nodeeditor.node_node.Node.onMarkedDirty` are being called. By default, these methods do nothing.
But still they are implemented in case you would like to override them and use in you own evaluation system.

