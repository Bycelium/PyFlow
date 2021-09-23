Serialization
=============

All of serializable classes derive from :class:`~nodeeditor.node_serializable.Serializable` class.
`Serializable` does create commonly used parameters for our classes. In our case it is just ``id``
attribute.

`Serializable` defines two methods which should be overriden in child classes:

- :py:func:`~nodeeditor.node_serializable.Serializable.serialize`
- :py:func:`~nodeeditor.node_serializable.Serializable.deserialize`

According to :ref:`coding-standards` we keep these two functions on the bottom of the class source code.

To contain all of the data we use ``OrderedDict`` instead of regular `dict`. Mainly because we want
to retain the order of parameters serialized in files.

Classes which derive from :class:`~nodeeditr.serializable.Serializable`:

- :class:`~nodeeditor.node_scene.Scene`
- :class:`~nodeeditor.node_node.Node`
- :class:`~nodeeditor.node_content_widget.QDMNodeContentWidget`
- :class:`~nodeeditor.node_edge.Edge`
- :class:`~nodeeditor.node_socket.Socket`