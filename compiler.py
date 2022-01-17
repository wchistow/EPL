"""Компилятор языка EPL версии 1.0."""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    WAIT = auto()
    CMD = auto()
    NUMBER = auto()
    STRING = auto()
    OPERATOR = auto()


def start_state(x):
    if x.isspace():
        return TokenType.WAIT
    elif x.isalpha():
        return TokenType.CMD
    elif x.isdigit():
        return TokenType.NUMBER
    elif x == "'":
        return TokenType.STRING
    elif x in '+-*/%':
        return TokenType.OPERATOR
    else:
        raise EPLSyntaxError(f'Синтаксическая ошибка: неверный символ "{x}"')


def tokenize(text):
    state = TokenType.WAIT
    current_token = ''
    for x in text:
        if state == TokenType.WAIT:
            state = start_state(x)
            if state == TokenType.OPERATOR:
                yield x
                state = TokenType.WAIT
            current_token = x
        elif state == TokenType.CMD:
            if not x.isalpha():
                yield current_token
                state = start_state(x)
                if state == TokenType.OPERATOR:
                    yield x
                    state = TokenType.WAIT
            else:
                current_token += x
        elif state == TokenType.NUMBER:
            if not x.isdigit():
                yield current_token
                state = start_state(x)
                if state == TokenType.OPERATOR:
                    yield x
                    state = TokenType.WAIT
            else:
                current_token += x
    if current_token:
        yield current_token


# Словарь команд.
built_in_funcs = {
    'ВВЕРХ': ['self.t.setheading(90)', 'self.t.forward(50)', 'check_hit_edge(self.t)'],
    'ВНИЗ': ['self.t.setheading(-90)', 'self.t.forward(50)', 'check_hit_edge(self.t)'],
    'ВПРАВО': ['self.t.setheading(0)', 'self.t.forward(50)', 'check_hit_edge(self.t)'],
    'ВЛЕВО': ['self.t.setheading(180)', 'self.t.forward(50)', 'check_hit_edge(self.t)'],
    'ПОДНЯТЬ': ['self.t.up()'],
    'ОПУСТИТЬ': ['self.t.down()'],
    'СБРОС': ['self.t.reset()'],
    'ОЧИСТИТЬ': ['self.t.clear()'],
    'ДОМОЙ': ['self.t.home()'],
    'СТЕРЕТЬ': ['del_text(self.t, self.canvas)']
}

checks = {
    'КРАЙ': 'check_edge(self.t)',
    'СИМВОЛ': 'is_symbol(self.t, "any")',
    'ПУСТО': 'not_symbol(self.t)',
    'СВОБОДНО': 'empty(self.t)',
    'НЕ': 'not',
    'И': 'and',
    'ИЛИ': 'or'
}

keywords = ['ЭТО', 'ПОВТОРИ', 'ЕСЛИ', 'НЕ', 'И', 'ИЛИ', 'ТО', 'ДЕЛАЙ', 'ИНАЧЕ', 'ПОКА', 'ПИШИ', 'КОНЕЦ']


@dataclass
class StackCell:
    name: str
    status: int
    code: str


class EPLException(Exception): pass


class EPLSyntaxError(EPLException): pass


class EPLNameError(EPLException): pass


class EPLValueError(EPLException): pass


class Compiler:
    def __init__(self):
        self.indent = ''
        self.pycode = []
        self.stack = [StackCell('main', 1, '')]
        self.user_funcs = {}
        self.handlers = {
            'func': self.handle_func_name,
            'loop': self.handle_loop_num,
            'while': self.handle_if_while_check,
            'if': self.handle_if_while_check,
            'write': self.handle_write_word
        }

        self.keywords_cells = {
            'ЭТО': ('func', 'def '),
            'ПОВТОРИ': ('loop', 'for i in range('),
            'ЕСЛИ': ('if', ''),
            'ПОКА': ('while', ''),
            'ПИШИ': ('write', 'write(self.t, '),
        }
        self.names = {
            'func': 'функция',
            'loop': 'цикл',
            'if': 'проверка',
            'while': 'цикл',
        }

    def translate(self, code: str):
        """
        Главная функция компиляции.
        принимает - код на языке EPL
        возвращает - код на языке Python.
        """
        for i, line in enumerate(get_lines(code), 1):
            try:
                for t in tokenize(line):

                    if self.stack[-1].status == 0:
                        self.handlers[self.stack[-1].name](t)

                    elif t in self.keywords_cells:
                        cell = self.keywords_cells[t]
                        if t == 'ЕСЛИ' or t == 'ПОКА':
                            self.stack.append(StackCell(cell[0], 0, cell[1]))
                        else:
                            self.stack.append(StackCell(cell[0], 0, self.indent + cell[1]))

                    elif t in built_in_funcs:
                        for string in built_in_funcs[t]:
                            self.pycode.append(f'{self.indent}{string}')

                    elif t in self.user_funcs:
                        self.pycode.append(self.indent + self.user_funcs[t])

                    elif t == 'ИНАЧЕ':
                        self.pycode.append(f'{self.indent[:-4]}else:')

                    elif t == 'КОНЕЦ':
                        if self.stack[-1].name == 'main':
                            raise EPLSyntaxError('Синтаксическая ошибка: конец без начала')
                        if self.pycode[-1].endswith(':'):
                            raise EPLSyntaxError(
                                f'Синтаксическая ошибка: {self.names[self.stack[-1].name]} без тела')
                        self.stack.pop()
                        self.indent = self.indent[:-4]

                    else:
                        raise EPLNameError(f'Не описана процедура с именем "{t}"')

            except EPLSyntaxError as e:
                raise EPLSyntaxError(e.args[0], i) from e
            except EPLNameError as e:
                raise EPLNameError(e.args[0], i) from e
            except EPLValueError as e:
                raise EPLValueError(e.args[0], i) from e

        return '\n'.join(self.pycode)

    def handle_func_name(self, token: str):
        if token in built_in_funcs or token in keywords:
            raise EPLNameError(f'Ошибка имени: имя "{token}" уже используется.')
        elif not token.isidentifier():
            raise EPLNameError(f'Не верное имя функции "{token}".')
        self.stack[-1].status = 1
        self.stack[-1].code += f'{token}(self):'
        self.pycode.append(self.stack[-1].code)
        self.user_funcs[token] = token + '(self)'
        self.indent += '    '

    def handle_loop_num(self, token):
        if not token.isdigit():
            raise EPLValueError('Цикл должен принимать целое не отрицательное число')
        self.stack[-1].status = 1
        self.stack[-1].code += str(int(float(token))) + '):'
        self.pycode.append(self.stack[-1].code)
        self.indent += '    '

    def handle_if_while_check(self, token):
        if token in checks:
            self.stack[-1].code += f'{checks[token]} '
        elif (self.stack[-1].name == 'while' and token == 'ДЕЛАЙ') or (self.stack[-1].name == 'if' and token == 'ТО'):
            try:
                compile(self.stack[-1].code, 'f', 'eval')
            except SyntaxError:
                raise EPLSyntaxError('Неверная проверка.')
            self.stack[-1].status = 1
            self.stack[-1].code += ':'
            if self.stack[-1].name == 'if':
                self.pycode.append(f'{self.indent}if ' + self.stack[-1].code)
            else:
                self.pycode.append(f'{self.indent}while ' + self.stack[-1].code)
            self.indent += '    '
        elif token.isdigit() or token.isalpha():
            if token in keywords:
                raise EPLSyntaxError(f'Неверное использование ключевого слова {token}.')
            self.stack[-1].code += f'is_symbol(self.t, "{token}") '

    def handle_write_word(self, token):
        if token in keywords:
            raise EPLSyntaxError(f'Неверное использование ключевого слова {token}.')
        self.stack[-1].status = 1
        self.stack[-1].code += f'"{token}", self.canvas)'
        self.pycode.append(self.stack[-1].code)


def get_lines(code: str):
    """Очищает код от комментариев."""
    for x in code.upper().splitlines():
        if '!' in x:
            x = x[:x.index('!')]
        yield x


def compilation(code: str):
    """Компилирует code."""
    comp = Compiler()
    return comp.translate(code)
