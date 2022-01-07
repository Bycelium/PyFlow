"""
This module defined Theme, a class that
contains the details of the theme
"""

import json
from PyQt5.Qsci import QsciLexerPython
from PyQt5.QtGui import QColor


class Theme:
    """Class holding the details of a specific theme."""

    def __init__(self, name: str, json_str: str = "{}"):
        """
        Create a new theme
        """
        json_obj = json.loads(json_str)
        known_properties = {
            "comment_color": "#797979",
            "string_color": "#CE9178",
            "function_color": "#DCDCAA",
            "keyword_color": "#569CD6",
            "classname_color": "#4EC9B0",
            "literal_color": "#7FB347",
            "operator_color": "#D8D8D8",
        }
        for (property_name, property_value) in known_properties.items():
            if property_name in json_obj:
                setattr(self, property_name, json_obj[property_name])
            else:
                setattr(self, property_name, property_value)
        self.name = name

    def apply_to_lexer(self, lexer: QsciLexerPython):
        """Make the given lexer follow the theme."""
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
