""" Unit tests for the opencodeblocks function parsing module. """

import pytest
from pytest_mock import MockerFixture
import pytest_check as check

from opencodeblocks.graphics.function_parsing import (find_kwarg_index, run_cell,
                                                      get_function_name,
                                                      get_signature,
                                                      extract_args,
                                                      execute_function,
                                                      find_kwarg_index)


class TestFunctionParsing:

    """Testing function_parsing functions"""

    def test_run_cell(self, mocker: MockerFixture):
        """ Test run_cell """
        check.equal(run_cell("print(10)"), '10\n')

    def test_get_function_name(self, mocker: MockerFixture):
        """ Test get_function_name """
        check.equal(get_function_name(
            "def function():\n   return 'Hello'"), 'function')
        check.equal(get_function_name(
            "#Hello\ndef function():\n   return 'Hello'\na = 10"), 'function')
        check.equal(get_function_name(
            "#Hello\ndef function(a,b=10):\n   return 'Hello'\na = 10"), 'function')

    def test_get_function_name_error(self, mocker: MockerFixture):
        """ Return ValueError if get_function_name has wrong input """
        with pytest.raises(ValueError):
            get_function_name("")
            get_function_name("#Hello")
            get_function_name("def function")

    def test_get_signature(self, mocker: MockerFixture):
        """ Test get_signature """
        mocker.patch(
            'opencodeblocks.graphics.function_parsing.run_cell', return_value="(a, b, c=10)\n")
        check.equal(get_signature(
            "def function(a,b, c=10):\n return None"), "(a, b, c=10)\n")

    def test_find_kwarg_index(self, mocker: MockerFixture):
        """ Test find_kwarg_index """
        check.equal(find_kwarg_index(['a', 'b', 'c=10']), 2)
        check.equal(find_kwarg_index([]), 0)

    def test_extract_args(self, mocker: MockerFixture):
        """ Test extract_args """
        mocker.patch(
            'opencodeblocks.graphics.function_parsing.get_signature', return_value="()\n")
        mocker.patch(
            'opencodeblocks.graphics.function_parsing.find_kwarg_index', return_value=0)
        check.equal(extract_args(
            "def function():\n   return 'Hello'"), ([], []))
        mocker.patch('opencodeblocks.graphics.function_parsing.get_signature',
                     return_value="(a,b,c = 10)\n")
        mocker.patch(
            'opencodeblocks.graphics.function_parsing.find_kwarg_index', return_value=2)
        check.equal(extract_args(
            "def function(a,b,c = 10):\n   return 'Hello'"), (["a", "b"], ["c=10"]))

    def test_extract_args_empty(self, mocker: MockerFixture):
        """ Return a couple of empty lists if signature is empty """
        mocker.patch('opencodeblocks.graphics.function_parsing.get_signature',
                     return_value="()\n")
        mocker.patch(
            'opencodeblocks.graphics.function_parsing.find_kwarg_index', return_value=None)
        check.equal(extract_args(
            "def function( ):\n   return 'Hello'"), ([], []))
        mocker.patch('opencodeblocks.graphics.function_parsing.get_signature',
                     return_value="()\n")
        mocker.patch(
            'opencodeblocks.graphics.function_parsing.find_kwarg_index', return_value=None)
        check.equal(extract_args(
            "def function():\n   return 'Hello'"), ([], []))

    def test_execute_function(self, mocker: MockerFixture):
        """ Test execute_function """
        mocker.patch('opencodeblocks.graphics.function_parsing.get_function_name',
                     return_value="function")
        mocker.patch(
            'opencodeblocks.graphics.function_parsing.run_cell', return_value="Out[1]: 25\n")
        check.equal(execute_function(
            "def function(a,b,c=10):\n return a+b+c", 10, 5), "Out[1]: 25\n")
