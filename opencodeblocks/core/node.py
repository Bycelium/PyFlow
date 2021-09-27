# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the pygraph Node """

from typing import List

class Node():
    def __init__(self, node_type:str, source:str="", title="Undefined block", metadata=None):
        self.title = title
        self.node_type = node_type
        self.source = source
        self.metadata = metadata if metadata is not None else {}

class CodeNode(Node):
    def __init__(self, source:str="", title="Undefined block",
            outputs:List[dict]=None, collapsed=True, scrolled=True, metadata=None):
        super().__init__(node_type="code", source=source, title=title, metadata=metadata)
        self.outputs = outputs if outputs is not None else []
        self.metadata.update({"collapsed": collapsed, "scrolled": scrolled})
