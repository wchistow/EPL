"""Графика."""

import tkinter
from turtle import TurtleScreen, RawTurtle
from sys import platform

import compiler
from functions import *
from lexer import EPLLexer


class Interface:
    def __init__(self):
        self.tk = tkinter.Tk()
        self.tk.title("EPL 1.1")
        # Окно ввода кода.
        self.lexer = EPLLexer()
        self.codeinput = tkinter.Text(self.tk, tabs=2)
        self.codeinput.grid(row=1, column=1, columnspan=2)
        self.codeinput.tag_configure("Token.Keyword", foreground="red")
        self.codeinput.tag_configure("Token.Text", foreground="black")
        self.codeinput.tag_configure("Token.Literal.String", foreground='cyan')
        self.codeinput.tag_configure("Token.Comment", foreground="grey")
        self.codeinput.tag_configure("Token.Name.Builtin", foreground="green")
        self.codeinput.bind('<Key>', lambda event: self.tk.after(20,
                            self.highlight_syntax))
        # Кнопка запуска.
        self.go_btn = tkinter.Button(self.tk, text='запустить', command=self.go)
        self.go_btn.grid(row=2, column=0)

        # Поле для рисования.
        self.canvas = tkinter.Canvas(self.tk, width=WIDTH, height=HEIGHT)
        self.canvas.grid(row=1, column=0)
        self.screen_draw = TurtleScreen(self.canvas)
        self.t = RawTurtle(self.screen_draw)

        self.modifier = 'Command' if platform == 'darwin' else 'Control'
        self.tk.bind(f'<{self.modifier}-n>', self.reset)
        self.tk.bind(f'<{self.modifier}-s>', self.save_file)
        self.tk.bind(f'<{self.modifier}-o>', self.open_file)
        self.tk.bind('<Escape>', self.ask_exit)

        self.tk.bind('<F1>', self.open_doc)

        self.create_menu(self.tk)

        self.is_compile = False

        tkinter.mainloop()

    def reset(self, evt):
        self.t.reset()
        self.t.up()
        reset_texts(self.canvas)
        self.codeinput.delete('1.0', 'end')

    def open_file(self, evt):
        try:
            open_f(self.codeinput)
        except (IOError, UnicodeDecodeError):
            pass

    def save_file(self, evt):
        try:
            save(self.codeinput.get('1.0', 'end'))
        except (IOError, UnicodeDecodeError):
            pass

    def ask_exit(self, evt=None):
        tk_exit = tkinter.Tk()
        tk_exit.title("Выход")
        label = tkinter.Label(tk_exit, text='Вы действительно хотите выйти?')
        label.pack()
        ok_button = tkinter.Button(tk_exit, text='Да', command=lambda: self.quit([tk_exit, self.tk]))
        undo_button = tkinter.Button(tk_exit, text='Нет', command=tk_exit.destroy)
        ok_button.pack(side=tkinter.LEFT)
        undo_button.pack(side=tkinter.RIGHT)

    def quit(self, tks: list[tkinter.Tk]):
        for tk in tks:
            tk.destroy()

    def open_doc(self, evt=None):
        tk = tkinter.Tk()
        tk.title("документация")
        show_doc = tkinter.Text(tk)
        with open('документация.md') as f:
            show_doc.insert('1.0', f.read())
        show_doc.grid(row=0, column=0)
        exit_btn = tkinter.Button(tk, text='закрыть', command=tk.destroy)
        exit_btn.grid(row=1, column=0)

    def highlight_syntax(self):
        for tag in ("Token.Keyword", "Token.Text", "Token.Literal.String",
                    "Token.Comment", "Token.Name.Builtin", "Token.Number"):
            self.codeinput.tag_remove(tag, "1.0", "end")
        name_entered = self.codeinput.get("1.0", "end")
        self.codeinput.mark_set("range_start", "1.0")
        for start, token, token_text in self.lexer.get_tokens_unprocessed(name_entered):
            self.codeinput.mark_set("range_end", f"range_start + {len(token_text)}c")
            self.codeinput.tag_add(str(token), 'range_start', 'range_end')
            self.codeinput.mark_set("range_start", "range_end")

    def create_menu(self, master):
        menu = tkinter.Menu()
        master.config(menu=menu)
        file_menu = tkinter.Menu(menu)
        file_menu.add_command(label='Новый', underline=0,
                              command=lambda: self.codeinput.insert('1.0', ''),
                              accelerator=self.modifier + '+N')
        if platform == 'darwin':
            master.createcommand('Сохранить', lambda: self.save_file(self.codeinput.get('1.0', 'end')))
            master.createcommand('Открыть', lambda: self.open_file(self.codeinput))
            master.createcommand('Выход', self.ask_exit)
        else:
            file_menu.add_separator()
            file_menu.add_command(label='Сохранить', underline=0,
                                  command=lambda: self.save_file(self.codeinput.get('1.0', 'end')),
                                  compound=tkinter.LEFT, accelerator=self.modifier + '+S')
            file_menu.add_separator()
            file_menu.add_command(label='Открыть', underline=0,
                                  command=lambda: self.open_file(self.codeinput),
                                  compound=tkinter.LEFT, accelerator=self.modifier + '+O')
            file_menu.add_separator()
            file_menu.add_command(label='Выход', underline=0,
                                  command=self.ask_exit,
                                  compound=tkinter.LEFT, accelerator='Escape')
        menu.add_cascade(label='Файл', underline=0,
                         menu=file_menu)

        help_menu = tkinter.Menu(menu)

        if platform == 'darwin':
            master.createcommand('Документация', self.open_doc)
        else:
            help_menu.add_command(label='Документация', underline=0,
                                  command=self.open_doc,
                                  compound=tkinter.LEFT, accelerator='F1')
        menu.add_cascade(label='Справка', underline=0,
                         menu=help_menu)

    def error(self, text, line_num=None):
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

    def compilation(self):
        """Запускает компиляцию."""
        text = self.codeinput.get('1.0', 'end')
        try:
            self.code = compiler.compilation(self.preprocess(repr(text)))
        except (compiler.EPLException) as e:
            self.error(e.args[0], line_num=e.args[1])
            self.is_compile = False
        else:
            self.is_compile = True

    def go(self):
        """Запускает скомпилированную программу."""
        self.compilation()

        self.t.reset()
        self.t.up()
        reset_texts(self.canvas)

        if self.is_compile:
            try:
                exec(self.code, globals(), locals())
            except BoundsError:
                self.error('Не могу!')
            except SyntaxError:
                self.error('Ошибка разработчиков.')
            except RecursionError:
                self.error('Бесконечная рекурсия.')

    def preprocess(self, code: str):
        """Превращает текст из Tkinter в нормальный текст."""
        return '\n'.join(x for x in code[1:-1].replace('\\t',
                         ' ').upper().split('\\N'))
