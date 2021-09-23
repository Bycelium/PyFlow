.. py:currentmodule:: nodeeditor.node_edge

:py:mod:`node\_edge` Module
============================

.. automodule:: nodeeditor.node_edge
    :members: EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER

    .. _edge-type-constants:

    Edge Type Constants
    -------------------

Edge Validators
---------------

Edge Validator can be registered to Edge class using its method
:class:`~nodeeditor.node_edge.Edge.registerEdgeValidator()`.

Each validator callback takes 2 params: `start_socket` and `end_socket`.
Validator also needs to return `True` or `False`. For example of validators
have a look in :mod:`node\_edge\_validators` module.

Here is an example how you can register the Edge Validator callbacks:

.. code-block:: python

    from nodeeditor.node_edge_validators import *

    Edge.registerEdgeValidator(edge_validator_debug)
    Edge.registerEdgeValidator(edge_cannot_connect_two_outputs_or_two_inputs)
    Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_same_node)



Edge Class
----------

.. autoclass:: nodeeditor.node_edge.Edge
    :members:
    :undoc-members:
    :show-inheritance:

