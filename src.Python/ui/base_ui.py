#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[RU]
Базовый класс для пользовательского интерфейса на основе curses.

[EN]
Base class for curses-based user interface.
"""

import curses
from abc import ABC, abstractmethod
from typing import Tuple


class BaseUI(ABC):
    """
    [RU]
    Базовый абстрактный класс для UI компонентов.

    [EN]
    Base abstract class for UI components.
    """

    def __init__(self, stdscr: curses.window):
        """
        [RU]
        Инициализация базового UI.

        Аргументы:
            stdscr (curses.window): Объект окна curses.

        Возвращает:
            None: Конструктор не возвращает значение.

        [EN]
        Initialize base UI.

        Args:
            stdscr (curses.window): Curses window object.

        Returns:
            None: Constructor does not return a value.
        """
        self.stdscr: curses.window = stdscr
        self.max_y: int = 0
        self.max_x: int = 0

        # Настройки curses
        self._setup_curses()

    def _setup_curses(self) -> None:
        """
        [RU]
        Настройка базовых параметров curses.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Setup basic curses parameters.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        curses.curs_set(1)
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.use_default_colors()
        self.stdscr.keypad(True)
        curses.set_escdelay(25)

    def get_terminal_size(self) -> Tuple[int, int]:
        """
        [RU]
        Получение текущего размера терминала.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            Tuple[int, int]: (высота, ширина) терминала

        [EN]
        Get current terminal size.

        Args:
            None: Function does not accept arguments.

        Returns:
            Tuple[int, int]: (height, width) of terminal
        """
        return self.stdscr.getmaxyx()

    def update_terminal_size(self) -> bool:
        """
        [RU]
        Обновление размера терминала и проверка изменений.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            bool: True если размер изменился, False иначе

        [EN]
        Update terminal size and check for changes.

        Args:
            None: Function does not accept arguments.

        Returns:
            bool: True if size changed, False otherwise
        """
        new_y, new_x = self.get_terminal_size()
        if new_y != self.max_y or new_x != self.max_x:
            self.max_y, self.max_x = new_y, new_x
            return True
        return False

    def cleanup(self) -> None:
        """
        [RU]
        Восстановление настроек терминала.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Restore terminal settings.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        try:
            curses.curs_set(1)
            curses.nocbreak()
            curses.echo()
            curses.endwin()  # Полное восстановление терминала
        except:
            pass

    @abstractmethod
    def draw(self) -> None:
        """
        [RU]
        Абстрактный метод отрисовки компонента.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Abstract method for component drawing.
        
        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        pass

    @abstractmethod
    def handle_input(self, key: int) -> bool:
        """
        [RU]
        Абстрактный метод обработки ввода.

        Аргументы:
            key (int): Код клавиши

        Возвращает:
            bool: True если ввод обработан, False иначе

        [EN]
        Abstract method for input handling.

        Args:
            key (int): Key code

        Returns:
            bool: True if input was handled, False otherwise
        """
        pass
