# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the Serializable base class """

from typing import Any, Dict, OrderedDict, Set


class Serializable:

    """Serializable base for serializable objects."""

    MANDATORY_FIELDS: OrderedDict = {}
    DEFAULT_DATA: Dict[str, Any] = {}

    def __init__(self):
        self.id = id(self)

    def serialize(self) -> OrderedDict:
        """Serialize the object as an ordered dictionary."""
        raise NotImplementedError()

    def deserialize(
        self, data: OrderedDict, hashmap: dict = None, restore_id=True
    ) -> None:
        """Deserialize the object from an ordered dictionary.

        Args:
            data: Dictionnary containing data do deserialize from.
            hashmap: Dictionnary mapping a hash code into knowed objects.
            restore_id: If True, the id will be restored using the given data.
                If False, a new id will be generated.

        """
        raise NotImplementedError()

    def complete_with_default(self, data: OrderedDict) -> None:
        """Add default data in place when fields are missing."""
        for key in self.MANDATORY_FIELDS:
            if key not in data:
                raise ValueError(f"{key} of the socket is missing")

        for key, val in self.DEFAULT_DATA.items():
            if key not in data:
                data[key] = val
