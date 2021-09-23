# -*- coding: utf-8 -*-
"""
A module containing the Edge Validator functions which can be registered as callbacks to
:class:`~nodeeditor.node_edge.Edge` class.

Example of registering Edge Validator callbacks:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can register validation callbacks once for example on the bottom of node_edge.py file or on the
application start with calling this:

.. code-block:: python

    from nodeeditor.node_edge_validators import *

    Edge.registerEdgeValidator(edge_validator_debug)
    Edge.registerEdgeValidator(edge_cannot_connect_two_outputs_or_two_inputs)
    Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_same_node)
    Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_different_type)


"""

DEBUG = False


def print_error(*args):
    """Helper method which prints to console if `DEBUG` is set to `True`"""
    if DEBUG: print("Edge Validation Error:", *args)

def edge_validator_debug(input: 'Socket', output: 'Socket') -> bool:
    """This will consider edge always valid, however writes bunch of debug stuff into console"""
    print("VALIDATING:")
    print(input, "input" if input.is_input else "output",  "of node", input.node)
    for s in input.node.inputs+input.node.outputs: print("\t", s, "input" if s.is_input else "output")
    print(output, "input" if input.is_input else "output", "of node", output.node)
    for s in output.node.inputs+output.node.outputs: print("\t", s, "input" if s.is_input else "output")

    return True

def edge_cannot_connect_two_outputs_or_two_inputs(input: 'Socket', output: 'Socket') -> bool:
    """Edge is invalid if it connects 2 output sockets or 2 input sockets"""
    if input.is_output and output.is_output:
        print_error("Connecting 2 outputs")
        return False

    if input.is_input and output.is_input:
        print_error("Connecting 2 inputs")
        return False

    return True

def edge_cannot_connect_input_and_output_of_same_node(input: 'Socket', output:'Socket') -> bool:
    """Edge is invalid if it connects the same node"""
    if input.node == output.node:
        print_error("Connecting the same node")
        return False

    return True

def edge_cannot_connect_input_and_output_of_different_type(input: 'Socket', output: 'Socket') -> bool:
    """Edge is invalid if it connects sockets with different colors"""

    if input.socket_type != output.socket_type:
        print_error("Connecting sockets with different colors")
        return False

    return True
