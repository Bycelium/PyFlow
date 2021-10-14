""" Unit tests for the opencodeblocks function parsing module. """

import pytest
from pytest_mock import MockerFixture
import pytest_check as check

from opencodeblocks.graphics.function_parsing import run_cell, get_function_name, get_signature, extract_args, execute_function

class TestFunctionParsing:
    def test_run_cell(self, mocker:MockerFixture):
        check.equal(run_cell("print(10)"), '10\n')
    
    def test_get_function_name(self, mocker:MockerFixture):
        check.equal(get_function_name("def function():\n   return 'Hello'"), 'function')
        check.equal(get_function_name("#Hello\ndef function():\n   return 'Hello'\na = 10"), 'function')
        check.equal(get_function_name("#Hello\ndef function(a,b=10):\n   return 'Hello'\na = 10"), 'function')

    def test_extract_args(self, mocker:MockerFixture):
        mocker.patch('opencodeblocks.graphics.function_parsing.get_signature', return_value="()\n")
        check.equal(extract_args("def function(a,b,c = 10):\n   return 'Hello'"), ([],[]))
        mocker.patch('opencodeblocks.graphics.function_parsing.get_signature', return_value="(a,b,c = 10)\n")
        check.equal(extract_args("def function(a,b,c = 10):\n   return 'Hello'"), (["a","b"],["c=10"]))