"""
This module provides `theme_manager()`,
a method that returns a handle to the theme manager of the application.

The theme manager provides the color scheme for the syntax highlighting
of the text areas containing code.
"""
import os
from typing import List

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtCore import pyqtSignal, QObject

from opencodeblocks.graphics.theme import Theme


class ThemeManager(QObject):
    """ Class loading theme files and providing the options set in those files """

    themeChanged = pyqtSignal()

    def __init__(self, parent=None):
        """ Load the default themes and the fonts available to construct the ThemeManager """
        super().__init__(parent)
        self._preferred_fonts = ["Inconsolata", "Roboto Mono", "Courier"]
        self.recommended_font_family = "Monospace"
        qfd = QFontDatabase()
        available_fonts = qfd.families()
        for font in self._preferred_fonts:
            if font in available_fonts:
                self.recommended_font_family = font
                break

        self._themes = []
        self._selected_theme_index = 0
        theme_path = "./themes"
        theme_paths = os.listdir(theme_path)
        for p in theme_paths:
            full_path = os.path.join(theme_path, p)
            if os.path.isfile(full_path) and full_path.endswith(".theme"):
                name = os.path.splitext(os.path.basename(p))[0]
                with open(full_path, 'r', encoding="utf-8") as f:
                    theme = Theme(name, f.read())
                    self._themes.append(theme)

    @property
    def selected_theme_index(self):
        return self._selected_theme_index

    @selected_theme_index.setter
    def selected_theme_index(self, value: int):
        self._selected_theme_index = value
        self.themeChanged.emit()

    def list_themes(self) -> List[str]:
        """ List the themes """
        return [theme.name for theme in self._themes]

    def current_theme(self) -> Theme:
        """ Return the current theme """
        return self._themes[self.selected_theme_index]


theme_handle = None


def theme_manager():
    """ Retreive the theme manager of the application """
    global theme_handle
    if theme_handle is None:
        theme_handle = ThemeManager()
    return theme_handle
