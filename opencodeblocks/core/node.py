# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the pygraph Node """

from typing import List, OrderedDict

from opencodeblocks.core.serializable import Serializable

class Node(Serializable):
    def __init__(self, node_type:str="base", source:str="", title="Undefined block", metadata=None):
        super().__init__()
        self.title = title
        self.node_type = node_type
        self.source = source
        self.metadata = metadata if metadata is not None else {}
        self.metadata.update({'title': self.title})

    def serialize(self) -> OrderedDict:
        metadata = OrderedDict(sorted(self.metadata.items()))
        return OrderedDict([
            ('id', self.id),
            ('node_type', self.node_type),
            ('metadata', metadata),
            ('source', self.source),
        ])

    def deserialize(self, data: OrderedDict) -> None:
        print(data)

class CodeNode(Node):
    def __init__(self, source:str="", title="Undefined block",
            outputs:List[dict]=None, collapsed=True, scrolled=True, metadata=None):
        super().__init__(node_type="code", source=source, title=title, metadata=metadata)
        self.outputs = outputs if outputs is not None else []
        self.metadata.update({"collapsed": collapsed, "scrolled": scrolled})

    def serialize(self) -> OrderedDict:
        base_data = super().serialize()
        base_data['outputs'] = self.outputs
        return base_data
