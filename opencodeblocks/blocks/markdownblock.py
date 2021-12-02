from PyQt5.Qsci import QsciLexerMarkdown, QsciScintilla
from opencodeblocks.blocks.block import OCBBlock

class OCBMarkdownBlock(OCBBlock):
    def __init__(self, **kwargs):
        """ 
            Create a new OCBMarkdownBlock, a block that renders markdown 
        """
        super().__init__(**kwargs)
        self.editor = QsciScintilla()
        self.lexer = QsciLexerMarkdown()
        self.editor.setLexer(self.lexer)

        self.splitter.addWidget(self.editor)
        self.holder.setWidget(self.root)