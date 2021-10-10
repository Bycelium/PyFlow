from typing import Any, Dict
from IPython.testing.globalipapp import get_ipython
from IPython.utils.io import capture_output
ip = get_ipython()

def run_cell(cell):
    """
    Executes a string of code in an IPython shell and returns the execution result
    :param cell: string containing Python code
    :type cell: String
    :return: execution result
    :rtype: Execution Result
    """
    with capture_output() as io:
        res = ip.run_cell(cell)
    res_out = io.stdout
    return res_out

def get_function_name(code):
    """
    Parses a string of code and returns the first function name it finds
    :param cell: string containing Python code
    :type cell: String
    :return: name of first defined function
    :rtype: String
    """
    start = 0
    end = 0
    for i in range(len(code)):
        if code[i:i+3] == "def":
            start = i+4
            break
    for i in range(start, len(code)):
        if code[i] == "(":
            end = i
            break
    return code[start:end]

def get_signature(code):
    """
    Returns the signature of a string of Python code defining a function
    For example: the signature of def hello(a,b,c=3) is "(a,b,c=3)"
    :param cell: string containing Python code
    :type cell: String
    :return: signature of first defined function
    :rtype: String
    """
    name = get_function_name(code)
    run_cell(code)
    run_cell("from inspect import signature")
    return run_cell("print(signature(" + name + "))")

def extract_args(code):
    """
    Returns the args and kwargs of a string of Python code defining a function
    For example: for def hello(a,b,c=3) it returns (["a","b"],["c=3"])
    :param cell: string containing Python code
    :type cell: String
    :return: (args,kwargs) of first defined function
    :rtype: Tuple
    """
    sig = get_signature(code)
    sig = str(sig)
    sig = sig[1:-2]
    if sig == "":
        return ([], [])
    sig = sig.replace(" ","")
    sig = sig.split(",")
    kwarg_index = len(sig)
    for i in range(len(sig)):
        if "=" in sig[i]:
            kwarg_index = i
            break
    return sig[:kwarg_index], sig[kwarg_index:]

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
