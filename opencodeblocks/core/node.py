# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the pygraph Node """

class Node():
    def __init__(self, title="Undefined block") -> None:
        self.title = title
        self.inputs = []
        self.outputs = []
