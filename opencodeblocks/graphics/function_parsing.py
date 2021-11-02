
""" Module for code parsing and code execution """

from typing import List, Tuple
from opencodeblocks.graphics.kernel import Kernel

kernel = Kernel()


def run_cell(cell: str) -> str:
    """
    Executes a piece of Python code in an ipython kernel, returns its last output

    Args:
        cell: String containing Python code

    Return:
        output in the last message sent by the kernel
    """
    return kernel.execute(cell)


def run_with_variable_output(cell: str) -> None:
    """
    This is a proof of concept to show that it is possible 
    to collect a variable output from a kernel execution

    Here the kernel executes the code and prints the output repeatedly
    For example: if cell="model.fit(...)", this would print the progress bar progressing

    Args:
        cell: String containing Python code
    """
    kernel.client.execute(cell)
    done = False
    while done == False:
        output, done = kernel.update_output()
        print(output)


def get_function_name(code: str) -> str:
    """
    Parses a string of code and returns the first function name it finds

    Args:
        code: String containing Python code

    Return:
        Name of first defined function
    """
    def_index = code.find("def")
    if def_index == -1:
        raise ValueError("'def' not found in source code")
    start_of_name = def_index + 4
    parenthesis_index = code.find("(", start_of_name)
    if parenthesis_index == -1:
        raise ValueError("'(' not found in source code")
    end_of_name = parenthesis_index
    return code[start_of_name:end_of_name]


def get_signature(code: str) -> str:
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


def find_kwarg_index(signature_couple: List[str]) -> int:
    """
    Returns the index delimiting the args and kwargs in a list of arguments
    Examples:
        find_kwwarg_index(['a','b','c=3']) -> 2
        find_kwwarg_index([]) -> None

    Args:
        list of Strings representing the arguments of a function

    Return:
        index delimiting the args and kwargs in a list of arguments

    """
    kwarg_index = len(signature_couple)
    for i, item in enumerate(signature_couple):
        if "=" in item:
            kwarg_index = i
            break
    return kwarg_index


def extract_args(code: str) -> Tuple[List[str], List[str]]:
    """
    Returns the args and kwargs of a string of Python code defining a function
    Examples:
        get_signature(def hello(a,b,c=3)...) -> "(a,b,c=3)"

    Args:
        code: String containing Python code

    Return:
        (args, kwargs) of first defined function

    """
    signature_string = get_signature(code)
    # Remove parentheses
    signature_string = signature_string[1:-2]
    signature_string = signature_string.replace(" ", "")
    if signature_string == "":
        return ([], [])
    signature_list = signature_string.split(",")
    kwarg_index = find_kwarg_index(signature_list)
    return signature_list[:kwarg_index], signature_list[kwarg_index:]


def execute_function(code: str, *args, **kwargs) -> str:
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
