from typing import Any, Dict
from IPython.testing.globalipapp import get_ipython
from IPython.utils.io import capture_output
ip = get_ipython()

def run_cell(cell:str):
    """
    Executes a string of code in an IPython shell and returns the execution result

    Args:
        cell: String containing Python code

    Return:
        Execution result of cell

    """
    with capture_output() as io:
        _ = ip.run_cell(cell)
    res_out = io.stdout
    return res_out

def get_function_name(code:str) -> str:
    """
    Parses a string of code and returns the first function name it finds

    Args:
        code: String containing Python code

    Return:
        Name of first defined function

    :param cell: string containing Python code
    :type cell: String
    :return: name of first defined function
    :rtype: String
    """
    start_of_name = 0
    end_of_name = 0
    for i in range(len(code)):
        if code[i:i+3] == "def":
            start_of_name = i+4
            break
    for i in range(start_of_name, len(code)):
        if code[i] == "(":
            end_of_name = i
            break
    return code[start_of_name:end_of_name]

def get_signature(code:str) -> str:
    """
    Returns the signature of a string of Python code defining a function
    For example: the signature of def hello(a,b,c=3) is "(a,b,c=3)"

    Args:
        code: String containing Python code

    Return:
        Signature of first defined function

    """
    name = get_function_name(code)
    run_cell(code)
    run_cell("from inspect import signature")
    return run_cell(f"print(signature({name}))")

def extract_args(code:str) -> tuple:
    """
    Returns the args and kwargs of a string of Python code defining a function
    For example: for def hello(a,b,c=3) it returns (["a","b"],["c=3"])

    Args:
        code: String containing Python code

    Return:
        (args, kwargs) of first defined function

    """
    signature = get_signature(code)
    signature_string = str(signature)
    signature_string = signature_string[1:-2]
    if signature_string == "":
        return ([], [])
    signature_string = signature_string.replace(" ","")
    signature_couple = signature_string.split(",")
    kwarg_index = len(signature_couple)
    for i, item in enumerate(signature_couple):
        if "=" in item:
            kwarg_index = i
            break
    return signature_couple[:kwarg_index], signature_couple[kwarg_index:]

def execute_function(code:str, *args, **kwargs) -> str:
    """
    Executes the function defined in code in an IPython shell and runs it fed by args and kwargs.
    Other arguments than the first are passed to the function when executing it.
    Keyword arguments are passed to the function when executing it.

    Args:
        code: String representing the function code to execute.

    Return:
        String representing the output given by the IPython shell when executing the function.

    """
    function_name = get_function_name(code)
    execution_code = f'{function_name}('
    for arg in args:
        execution_code += f'{arg},'
    for name, value in kwargs.items():
        execution_code += f'{name}={value},'

    run_cell(code)
    return run_cell(execution_code + ')')