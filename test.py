import unittest

from compiler import Compiler, EPLSyntaxError, EPLNameError, EPLValueError


class TestCompiler(unittest.TestCase):

    def setUp(self):
        self.comp = Compiler()

    def test_up_down_right_left(self):
        """Тестирует вверх, вниз, вправо, влево."""
        code = 'вверх вниз вправо влево'
        good_ans = 'self.t.setheading(90)\nself.t.forward(50)\ncheck_hit_edge(self.t)\n'  # вверх
        good_ans += 'self.t.setheading(-90)\nself.t.forward(50)\ncheck_hit_edge(self.t)\n'  # вниз
        good_ans += 'self.t.setheading(0)\nself.t.forward(50)\ncheck_hit_edge(self.t)\n'  # вправо
        good_ans += 'self.t.setheading(180)\nself.t.forward(50)\ncheck_hit_edge(self.t)'  # влево
        # trans_code = self.comp.translate(code)
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_up_down_pen(self):
        """Тестирует поднимание и опускание пера."""
        code = 'поднять опустить'
        good_ans = 'self.t.up()\nself.t.down()'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_reset_clear_home_del(self):
        """Тестирует сброс, очистить, домой, стереть."""
        code = 'сброс очистить домой стереть'
        good_ans = 'self.t.reset()\nself.t.clear()\nself.t.home()\ndel_text(self.t, self.canvas)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_write(self):
        """Тестирует 'пиши а' и комментарий."""
        code = 'пиши а'
        good_ans = 'write(self.t, "А", self.canvas)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_comment(self):
        self.assertEqual(self.comp.translate('! hello'), '')

    def test_define_func(self):
        """Тестирует определение функции."""
        code = 'это имя вверх конец имя'
        good_ans = 'def ИМЯ():\n'
        good_ans += '    self.t.setheading(90)\n    self.t.forward(50)\n    check_hit_edge(self.t)\n'
        good_ans += 'ИМЯ()'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_loop(self):
        """Тестирует цикл."""
        code = 'повтори 3 вправо конец'
        good_ans = 'for i in range(3):\n'
        good_ans += '    self.t.setheading(0)\n    self.t.forward(50)\n    check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    # Тесты проверок ----------
    def test_check_edge(self):
        code = 'если край то вниз конец'
        good_ans = 'if check_edge(self.t) :\n'
        good_ans += '    self.t.setheading(-90)\n    self.t.forward(50)\n    check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_not_check_edge(self):
        code = 'если не край то вниз конец'
        good_ans = 'if not check_edge(self.t) :\n'
        good_ans += '    self.t.setheading(-90)\n    self.t.forward(50)\n    check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_is_symbol(self):
        code = 'если символ то вниз конец'
        good_ans = 'if is_symbol(self.t, "any") :\n'
        good_ans += '    self.t.setheading(-90)\n    self.t.forward(50)\n    check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_not_is_symbol(self):
        code = 'если не символ то вниз конец'
        good_ans = 'if not is_symbol(self.t, "any") :\n'
        good_ans += '    self.t.setheading(-90)\n    self.t.forward(50)\n    check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_empty(self):
        code = 'если пусто то вниз конец'
        good_ans = 'if not_symbol(self.t) :\n'
        good_ans += '    self.t.setheading(-90)\n    self.t.forward(50)\n    check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_not_empty(self):
        code = 'если не пусто то вниз конец'
        good_ans = 'if not not_symbol(self.t) :\n'
        good_ans += '    self.t.setheading(-90)\n    self.t.forward(50)\n    check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_if_else(self):
        code = 'если край то вверх иначе вниз конец'
        good_ans = 'if check_edge(self.t) :\n'
        good_ans += '    self.t.setheading(90)\n    self.t.forward(50)\n    check_hit_edge(self.t)\n'
        good_ans += 'else:\n'
        good_ans += '    self.t.setheading(-90)\n    self.t.forward(50)\n    check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_is_letter(self):
        code = 'если а то вверх конец'
        good_ans = 'if is_symbol(self.t, "А") :\n'
        good_ans += '    self.t.setheading(90)\n    self.t.forward(50)\n    check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_or(self):
        code = 'если край или пусто то вниз конец'
        good_ans = 'if check_edge(self.t) or not_symbol(self.t) :\n'
        good_ans += '    self.t.setheading(-90)\n    self.t.forward(50)\n    check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_not_symbol(self):
        code = 'если свободно то вниз конец'
        good_ans = 'if empty(self.t) :\n'
        good_ans += '    self.t.setheading(-90)\n    self.t.forward(50)\n    check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_while(self):
        """Тестирует цикл пока."""
        code = 'пока не край то вверх конец'
        good_ans = 'while not check_edge(self.t) :\n'
        good_ans += '    self.t.setheading(90)\n    self.t.forward(50)\n    check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    def test_nested(self):
        code = 'это имя если край то вниз конец конец'
        good_ans = 'def ИМЯ():\n    if check_edge(self.t) :\n'
        good_ans += '        self.t.setheading(-90)\n        self.t.forward(50)\n        check_hit_edge(self.t)'
        self.assertEqual(self.comp.translate(code), good_ans)

    # Тесты ошибок ----------
    def test_invalid_symbol(self):
        """Тестирует неверный символ."""
        code = ';'
        with self.assertRaisesRegex(EPLSyntaxError, 'Синтаксическая ошибка: неверный символ ";"'):
            self.comp.translate(code)

    def test_end_without_begin(self):
        """Тестирует конец без начала."""
        code = 'конец'
        with self.assertRaisesRegex(EPLSyntaxError, 'Синтаксическая ошибка: конец без начала'):
            self.comp.translate(code)

    def test_func_without_body(self):
        """Тестирует функцию без тела."""
        code = 'это имя конец'
        with self.assertRaisesRegex(EPLSyntaxError, 'Синтаксическая ошибка: функция без тела'):
            self.comp.translate(code)

    def test_undefined_name(self):
        """Тестирует неверное имя."""
        code = 'h'
        with self.assertRaisesRegex(EPLNameError, 'Не описана процедура с именем "H"'):
            self.comp.translate(code)

    def test_used_name(self):
        """Тестирует используемое имя."""
        code = 'это вверх вниз конец'
        with self.assertRaisesRegex(EPLNameError, 'Ошибка имени: имя "ВВЕРХ" уже используется.'):
            self.comp.translate(code)

    def test_invalid_func_name(self):
        """Тестирует неверное имя функции."""
        code = 'это 5 вниз конец'
        with self.assertRaisesRegex(EPLNameError, 'Не верное имя функции "5".'):
            self.comp.translate(code)

    def test_not_num_in_loop(self):
        """Тестирует цикл не с числом."""
        code = 'повтори п вниз конец'
        with self.assertRaisesRegex(EPLValueError, 'Цикл должен принимать целое не отрицательное число'):
            self.comp.translate(code)

    def test_loop_num_less_0(self):
        code = 'повтори -2 вниз конец'
        with self.assertRaisesRegex(EPLValueError, 'Цикл должен принимать целое не отрицательное число'):
            self.comp.translate(code)

    def test_invalid_check(self):
        code = 'если не то вниз конец'
        with self.assertRaisesRegex(EPLSyntaxError, 'Неверная проверка.'):
            self.comp.translate(code)


unittest.main()
