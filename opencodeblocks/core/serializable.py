# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the Serializable base class """

class Serializable():

    def serialize(self) -> dict:
        raise NotImplementedError()

    def deserialize(self, data:dict) -> None:
        raise NotImplementedError()
