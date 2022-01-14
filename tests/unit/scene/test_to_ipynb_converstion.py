# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

"""Unit tests for the conversion to ipynb."""

from typing import Dict, List, OrderedDict
from pytest_mock import MockerFixture
import pytest_check as check
import json

from pyflow.scene.to_ipynb_conversion import ipyg_to_ipynb
from pyflow.scene.ipynb_conversion_constants import BLOCK_TYPE_TO_NAME


class TestToIpynbConversion:

    """Conversion to .ipynb"""

    def test_empty_data(self, mocker: MockerFixture):
        """should return an empty list of cells when the ipyg graph is empty."""
        ipynb_data = ipyg_to_ipynb({"blocks": [], "edges": []})
        check.equal("cells" in ipynb_data, True)
        check.equal(type(ipynb_data["cells"]), list)
        check.equal(len(ipynb_data["cells"]), 0)

    def test_simple_flow_example(self, mocker: MockerFixture):
        """should return the right number of cells in a right order on the mnist example."""

        file_path = "./tests/assets/simple_flow.ipyg"
        ipyg_data: OrderedDict = {}
        with open(file_path, "r", encoding="utf-8") as file:
            ipyg_data = json.loads(file.read())
        ipynb_data = ipyg_to_ipynb(ipyg_data)

        check.equal("cells" in ipynb_data, True)
        check.equal(type(ipynb_data["cells"]), list)
        check.equal(len(ipynb_data["cells"]), 7)

        # Compute the order in which the cells have been placed
        # The first line of each block is "#{nb}"
        results_inverse_order: List[int] = [
            int(cell["source"][0][1:2]) for cell in ipynb_data["cells"]
        ]
        result_order: List[int] = [0] * 7
        for i in range(7):
            result_order[results_inverse_order[i]] = i

        # Sufficient conditions for the ipynb notebook to execute properly
        check.equal(result_order[0], 0)
        check.equal(
            result_order[2] < result_order[3] < result_order[4] < result_order[5], True
        )
        check.equal(result_order[4] < result_order[6], True)
