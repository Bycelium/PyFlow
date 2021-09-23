Event system
============

Nodeeditor uses its own events (and tries to avoid using ``pyqtSignal``) to handle logic
happening inside the Scene. If a class does handle some events, they are usually described
at the top of the page in this documentation.

Any of the events is subscribable to and the methods for registering callback are called:

.. code-block:: python

    add<EventName>Listener(callback)

You can register to any of these events any time.

Events used in NodeEditor:
--------------------------

:class:`~nodeeditor.node_scene.Scene`
+++++++++++++++++++++++++++++++++++++

.. include:: rst/events_scene.rst


:class:`~nodeeditor.node_scene_history.SceneHistory`
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. include:: rst/events_scene_history.rst
