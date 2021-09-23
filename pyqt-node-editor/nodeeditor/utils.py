# -*- encoding: utf-8 -*-
"""
Module with some helper functions
"""
import traceback
from qtpy.QtCore import QFile
from qtpy.QtWidgets import QApplication
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4).pprint


def dumpException(e=None):
    """
    Prints out an Exception message with a traceback to the console

    :param e: Exception to print out
    :type e: Exception
    """
    # print("%s EXCEPTION:" % e.__class__.__name__, e)
    # traceback.print_tb(e.__traceback__)
    traceback.print_exc()


def loadStylesheet(filename: str):
    """
    Loads an qss stylesheet to the current QApplication instance

    :param filename: Filename of qss stylesheet
    :type filename: str
    """
    print('STYLE loading:', filename)
    file = QFile(filename)
    file.open(QFile.ReadOnly | QFile.Text)
    stylesheet = file.readAll()
    QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))

def loadStylesheets(*args):
    """
    Loads multiple qss stylesheets. Concatenates them together and applies the final stylesheet to the current QApplication instance

    :param args: variable number of filenames of qss stylesheets
    :type args: str, str,...
    """
    res = ''
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        res += "\n" + str(stylesheet, encoding='utf-8')
    QApplication.instance().setStyleSheet(res)
