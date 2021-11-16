"""
This module provides several functions to define the
appearance of the editing sections
"""
import os, json
from PyQt5.QtGui import QFontDatabase, QColor
from PyQt5.Qsci import QsciLexerPython

class Theme:
    """ Class holding the details of a specific theme"""
    def __init__(self, name: str,json_str: str = "{}"):
        json_obj = json.loads(json_str)
        known_properties = {
            "comment_color":"#797979",
            "string_color":"#CE9178",
            "function_color":"#DCDCAA",
            "keyword_color":"#569CD6",
            "classname_color":"#4EC9B0",
            "literal_color":"#7FB347",
            "operator_color":"#D8D8D8"
        }
        for p in known_properties:
            if p in json_obj:
                setattr(self,p,json_obj[p])
            else:
                setattr(self,p,known_properties[p])
        self.name = name

    def apply_to_lexer(self, lexer: QsciLexerPython):
        lexer.setDefaultPaper(QColor("#1E1E1E"))
        lexer.setDefaultColor(QColor("#D4D4D4"))

        string_types = [
            QsciLexerPython.SingleQuotedString,
            QsciLexerPython.DoubleQuotedString,
            QsciLexerPython.UnclosedString,
            QsciLexerPython.SingleQuotedFString,
            QsciLexerPython.TripleSingleQuotedString,
            QsciLexerPython.TripleDoubleQuotedString,
            QsciLexerPython.TripleSingleQuotedFString,
            QsciLexerPython.TripleDoubleQuotedFString,
        ]

        for string_type in string_types:
            lexer.setColor(QColor(self.string_color), string_type)

        lexer.setColor(QColor(self.function_color), QsciLexerPython.FunctionMethodName)
        lexer.setColor(QColor(self.keyword_color), QsciLexerPython.Keyword)
        lexer.setColor(QColor(self.classname_color), QsciLexerPython.ClassName)
        lexer.setColor(QColor(self.literal_color), QsciLexerPython.Number)
        lexer.setColor(QColor(self.operator_color), QsciLexerPython.Operator)
        lexer.setColor(QColor(self.comment_color), QsciLexerPython.CommentBlock)
        lexer.setColor(QColor(self.comment_color), QsciLexerPython.Comment)

class ThemeManager:
    """ Class loading theme files and providing the options set in those files """
    def __init__(self):
        """ Load the default themes and the fonts available to construct the ThemeManager """
        self._preferred_fonts = ["Inconsolata","Roboto Mono","Courier"]
        self.recommended_font_family = "Monospace"
        qfd = QFontDatabase()
        available_fonts = qfd.families()
        for font in self._preferred_fonts:
            if font in available_fonts:
                self.recommended_font_family = font
                break

        self._themes = []
        self.selected_theme_index = 0
        theme_path = "./themes"
        theme_paths = os.listdir(theme_path)
        for p in theme_paths:
            full_path = os.path.join(theme_path,p)
            if os.path.isfile(full_path) and full_path.endswith(".theme"):
                name = os.path.splitext(os.path.basename(p))[0]
                theme = Theme(name, open(full_path,'r').read())
                self._themes.append(theme)

    def list_themes(self) -> list[str]:
        return [theme.name for theme in self._themes]
    def current_theme(self) -> Theme:
        return self._themes[self.selected_theme_index]

theme_handle = None
def theme_manager():
    """ Retreive the theme manager of the application """
    global theme_handle
    if theme_handle == None:
        theme_handle = ThemeManager()
    return theme_handle