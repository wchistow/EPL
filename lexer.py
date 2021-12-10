import re

from pygments.lexer import RegexLexer, words
from pygments.token import *

from compiler import keywords, checks, built_in_funcs


class EPLLexer(RegexLexer):
    name = 'EPL'

    flags = re.IGNORECASE

    tokens = {
        'root': [
            (words(built_in_funcs, suffix=r'\b'), Name.Builtin),
            (words(keywords, suffix=r'\b'), Keyword),
            (words(checks, suffix=r'\b'), String),
            (r'\b\d+', Number),
            (r'\w+', Text),
            (r'\s+', Text),
            (r'!.*', Comment),
        ]
    }


if __name__ == '__main__':
    code = 'ЕСЛИ НЕ КРАЙ ТО ! Проверка.\n  квадрат \n   ВВЕРХ\nКОНЕЦ'

    # highlight(code, EPLLexer(), GifImageFormatter(), outfile='out.gif')
    lexer = EPLLexer()
    for start, token, text in lexer.get_tokens_unprocessed(code):
        print(start, start + len(text), token)
