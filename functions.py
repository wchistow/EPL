"""
Этот модуль содержит функции,
которые необходимы для работы кода,
скомпилированного модулем compiler.
"""

from tkinter import filedialog


texts = {}

WIDTH = 400
HEIGHT = 400


class BoundsError(Exception):
    pass


def check_hit_edge(t):
    """Проверяет столкновение черепашки с краем."""
    if t.xcor() > WIDTH / 2:
        t.backward(50)
        raise BoundsError('Не могу!')
    elif t.xcor() < -WIDTH / 2:
        t.backward(50)
        raise BoundsError('Не могу!')
    elif t.ycor() > HEIGHT / 2:
        t.backward(50)
        raise BoundsError('Не могу!')
    elif t.ycor() < -HEIGHT / 2:
        t.backward(50)
        raise BoundsError('Не могу!')


def check_edge(t):
    """
    Если черепашка столкнулась с краем
    возвращает True.
    """
    if t.xcor() > WIDTH / 2 - 30:
        return True
    elif t.xcor() < -WIDTH / 2 - 30:
        return True
    elif t.ycor() > HEIGHT / 2 - 30:
        return True
    elif t.ycor() < -HEIGHT / 2 - 30:
        return True


def reset_texts(canvas):
    """Удаляет весь текст с поля."""
    global texts
    for v in texts.values():
        canvas.delete(v[0])
    texts = {}


def write(t, text, canvas):
    global texts
    x = round(t.xcor())
    y = round(t.ycor())
    if (x, y) in texts:
        canvas.delete(texts[x, y][0])
    s = canvas.create_text(x, -y, text=text)
    texts[x, y] = (s, text)


def del_text(t, canvas):
    x = round(t.xcor())
    y = round(t.ycor())
    if (x, y) in texts:
        canvas.delete(texts[x, y])
        del texts[x, y]


def is_symbol(t, symbol):
    x = t.xcor()
    y = t.ycor()
    if symbol == 'any':
        if (x, y) in texts:
            return True
    else:
        if (x, y) in texts and texts[x, y][-1] == symbol:
            return True
    return False


def empty(t):
    return not is_symbol(t, 'any') and not check_edge(t)


def not_symbol(t):
    return not is_symbol(t, 'any')


def save(text):
    """Сохраняет файл."""
    file = filedialog.asksaveasfile()
    if file:
        file.write(text)
        file.close()


def open_f(codeinput):
    """Открывает файл."""
    file = filedialog.askopenfile()
    if file:
        codeinput.delete('1.0', 'end')
        codeinput.insert('1.0', file.read())
        file.close()
