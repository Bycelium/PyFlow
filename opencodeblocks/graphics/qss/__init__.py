# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the OCB qss and styles. """

from typing import List

from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QApplication

from opencodeblocks.graphics.qss import dark_resources


def loadStylesheets(filenames: List[str]):
    styles = ''
    for filename in filenames:
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        styles += "\n" + str(stylesheet, encoding='utf-8')
    QApplication.instance().setStyleSheet(styles)
