Welcome to PyQtNodeEditor
==========================

.. image:: https://badge.fury.io/py/nodeeditor.svg
    :target: https://badge.fury.io/py/nodeeditor

.. image:: https://readthedocs.org/projects/pyqt-node-editor/badge/?version=latest
    :target: https://pyqt-node-editor.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


This package was created from the Node Editor written in PyQt5. The intention was to create a tutorial series
describing the path to create a reusable nodeeditor which can be used in different projects.
The tutorials are published on youtube for free. The full list of tutorials can be located here:
https://www.blenderfreak.com/tutorials/node-editor-tutorial-series/

Features
--------

- provides full framework for creating customizable graph, nodes, sockets and edges
- full support for undo / redo and serialization into files in a VCS friendly way
- support for implementing evaluation logic
- hovering effects, dragging edges, cutting lines and a bunch more...
- provided 2 examples on how node editor can be implemented

Requirements
------------

- Python 3.x
- PyQt5 or PySide2 (using wrapper QtPy)

Installation
------------

::

    $ pip install nodeeditor


Or directly from source code to get the latest version


::

    $ pip install git+https://gitlab.com/pavel.krupala/pyqt-node-editor.git


Or download the source code from gitlab::

    git clone https://gitlab.com/pavel.krupala/pyqt-node-editor.git


Screenshots
-----------

.. image:: https://www.blenderfreak.com/media/products/NodeEditor/screenshot-calculator.png
  :alt: Screenshot of Calculator Example

.. image:: https://www.blenderfreak.com/media/products/NodeEditor/screenshot-example.png
  :alt: Screenshot of Node Editor

Other links
-----------

- `Documentation <https://pyqt-node-editor.readthedocs.io/en/latest/>`_

- `Contribute <https://gitlab.com/pavel.krupala/pyqt-node-editor/blob/master/CONTRIBUTING.md>`_

- `Issues <https://gitlab.com/pavel.krupala/pyqt-node-editor/issues>`_

- `Merge requests <https://gitlab.com/pavel.krupala/pyqt-node-editor/merge_requests>`_

- `Changelog <https://gitlab.com/pavel.krupala/pyqt-node-editor/blob/master/CHANGES.rst>`_