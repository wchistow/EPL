"""Графика."""

import tkinter
from sys import platform
from time import time
from turtle import TurtleScreen, RawTurtle

import compiler
from functions import *
from lexer import EPLLexer


def create_interface():
    """Строит интерфейс."""
    global t, codeinput, canvas, lexer
    tk = tkinter.Tk()
    tk.title("EPL 1.0")
    # Окно ввода кода.
    lexer = EPLLexer()
    codeinput = tkinter.Text(tk, tabs=2)
    codeinput.grid(row=1, column=1, columnspan=2)
    codeinput.tag_configure("Token.Keyword", foreground="red")
    codeinput.tag_configure("Token.Text", foreground="black")
    codeinput.tag_configure("Token.Literal.String", foreground='cyan')
    codeinput.tag_configure("Token.Comment", foreground="grey")
    codeinput.tag_configure("Token.Name.Builtin", foreground="green")
    codeinput.bind('<Key>', lambda event: tk.after(20, highlight_syntax))
    # Кнопка запуска.
    go_btn = tkinter.Button(tk, text='запустить', command=go)
    go_btn.grid(row=2, column=1)
    # Кнопка проверки.
    comp = tkinter.Button(tk, text='проверить', command=compilation)
    comp.grid(row=2, column=2)

    create_menu(tk)

    # Поле для рисования.
    canvas = tkinter.Canvas(tk, width=WIDTH, height=HEIGHT)
    canvas.grid(row=1, column=0)
    screen_draw = TurtleScreen(canvas)
    t = RawTurtle(screen_draw)

    modifier = 'Command' if platform == 'darwin' else 'Control'
    tk.bind(f'<{modifier}-n>', reset)
    tk.bind(f'<{modifier}-s>', save_file)
    tk.bind(f'<{modifier}-o>', open_file)
    tk.bind('<Escape>', on_exit)

    tk.bind('<F1>', open_doc)

    tkinter.mainloop()


def reset(evt):
    t.reset()
    t.up()
    reset_texts(canvas)
    codeinput.delete('1.0', 'end')


def open_file(evt):
    try:
        open_f(codeinput)
    except (IOError, UnicodeDecodeError):
        pass


def save_file(evt):
    try:
        save(codeinput.get('1.0', 'end'))
    except (IOError, UnicodeDecodeError):
        pass


def on_exit(evt=None):
    exit_of_course = tkinter.Tk()
    exit_of_course.title("Выход")
    label = tkinter.Label(exit_of_course, text='Вы действительно хотите выйти?')
    label.pack()
    ok_button = tkinter.Button(exit_of_course, text='Да', command=exit, activebackground='red')
    undo_button = tkinter.Button(exit_of_course, text='Нет', command=exit_of_course.destroy,
                                 activebackground='cyan')
    ok_button.pack(side=tkinter.LEFT)
    undo_button.pack(side=tkinter.RIGHT)


def open_doc(evt=None):
    tk = tkinter.Tk()
    tk.title("документация")
    show_doc = tkinter.Text(tk)
    with open('документация.txt') as f:
        show_doc.insert('1.0', f.read())
    show_doc.pack()


def highlight_syntax():
    for tag in ("Token.Keyword", "Token.Text", "Token.Literal.String",
                "Token.Comment", "Token.Name.Builtin", "Token.Number"):
        codeinput.tag_remove(tag, "1.0", "end")
    name_entered = codeinput.get("1.0", "end")
    codeinput.mark_set("range_start", "1.0")
    for start, token, token_text in lexer.get_tokens_unprocessed(name_entered):
        codeinput.mark_set("range_end", f"range_start + {len(token_text)}c")
        codeinput.tag_add(str(token), 'range_start', 'range_end')
        codeinput.mark_set("range_start", "range_end")


def create_menu(master):
    menu = tkinter.Menu()
    master.config(menu=menu)
    modifier = 'Command' if platform == 'darwin' else 'Control'
    file_menu = tkinter.Menu(menu)
    file_menu.add_command(label='Новый', underline=0,
                          command=lambda: codeinput.insert('1.0', ''),
                          accelerator=modifier + '+N')
    if platform == 'darwin':
        master.createcommand('Сохранить', lambda: save(codeinput.get('1.0', 'end')))
        master.createcommand('Открыть', lambda: open_f(codeinput))
        master.createcommand('Выход', on_exit)
    else:
        file_menu.add_separator()
        file_menu.add_command(label='Сохранить', underline=0,
                              command=lambda: save(codeinput.get('1.0', 'end')),
                              compound=tkinter.LEFT, accelerator=modifier + '+S')
        file_menu.add_separator()
        file_menu.add_command(label='Открыть', underline=0,
                              command=lambda: open_f(codeinput),
                              compound=tkinter.LEFT, accelerator=modifier + '+O')
        file_menu.add_separator()
        file_menu.add_command(label='Выход', underline=0,
                              command=on_exit,
                              compound=tkinter.LEFT, accelerator='Escape')
    menu.add_cascade(label='Файл', underline=0,
                     menu=file_menu)

    help_menu = tkinter.Menu(menu)

    if platform == 'darwin':
        master.createcommand('Документация', open_doc)
    else:
        help_menu.add_command(label='Документация', underline=0,
                              command=open_doc,
                              compound=tkinter.LEFT, accelerator='F1')
    menu.add_cascade(label='Справка', underline=0,
                     menu=help_menu)


def error(text, line_num=None):
    """Выводит сообщение об ошибке."""
    tke = tkinter.Tk()
    tke.title('Ошибка')
    canvas = tkinter.Canvas(tke, width=180 + len(text) * 8, height=100)
    canvas.grid(row=0, column=0)
    ok = tkinter.Button(tke, text='OK', command=tke.destroy)
    ok.grid(row=1, column=0)
    msg = f'Строка {line_num}\n' if line_num else ''
    msg += text
    canvas.create_text(30 + len(text) * 5, 50, text=msg,
                       fill='red', font=('Helvetika', -15))


def good_compilation(t):
    """Выводит сообщение об успешной компиляции."""
    tkg = tkinter.Tk()
    tkg.title('Успешная проверка')
    canvas = tkinter.Canvas(tkg, width=400, height=100)
    canvas.grid(row=0, column=0)
    ok = tkinter.Button(tkg, text='OK', command=tkg.destroy)
    ok.grid(row=1, column=0)
    canvas.create_text(200, 50, text=f'Проверка прошла успешно!\nВремя - {t}мкс',
                       fill='green', font=('Helvetika', -20))


is_compile = False


def compilation():
    """Запускает компиляцию."""
    global code, is_compile
    t1 = time()
    text = codeinput.get('1.0', 'end')
    try:
        code = compiler.compilation(preprocess(repr(text)))
        is_compile = True
    except (compiler.EPLSyntaxError, compiler.EPLNameError, compiler.EPLValueError) as e:
        error(e.args[0])
    else:
        t = int((time() - t1) * 1000000)
        good_compilation(t)


def go():
    """Запускает скомпилированную программу."""
    if is_compile:
        t.reset()
        t.up()
        reset_texts(canvas)
        try:
            exec(code, globals())
        except BoundsError:
            error('Не могу!')
        except SyntaxError:
            error('Ошибка разработчиков.')
        except RecursionError:
            error('Бесконечная рекурсия.')


def preprocess(code: str):
    """Превращает текст из Tkinter в нормальный текст."""
    return '\n'.join(x for x in code[1:-1].replace('\\t', ' ').upper().split('\\N'))
