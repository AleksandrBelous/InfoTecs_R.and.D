#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[RU]
Менеджер окон для curses интерфейса.

[EN]
Window manager for curses interface.
"""

import curses
from .base_ui import BaseUI


class WindowManager(BaseUI):
    """
    [RU]
    Менеджер окон curses для управления геометрией и созданием окон.

    [EN]
    Curses window manager for geometry and window creation.
    """

    def __init__(self, stdscr: curses.window):
        """
        [RU]
        Инициализация менеджера окон.

        Аргументы:
            stdscr (curses.window): Объект окна curses.

        Возвращает:
            None: Конструктор не возвращает значение.

        [EN]
        Initialize window manager.

        Args:
            stdscr (curses.window): Curses window object.

        Returns:
            None: Constructor does not return a value.
        """
        super().__init__(stdscr)

        # Окна интерфейса
        self.status_block: curses.window = curses.newwin(0, 0)
        self.messages_block: curses.window = curses.newwin(0, 0)
        self.input_block: curses.window = curses.newwin(0, 0)

        # Инициализация размеров
        self.max_y, self.max_x = self.get_terminal_size()
        self._create_windows()

    def _create_windows(self) -> None:
        """
        [RU]
        Создание/пересоздание окон интерфейса.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Create/recreate interface windows.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        # Статусная строка (верхняя)
        self.status_block = curses.newwin(1, self.max_x, 0, 0)

        # Блок сообщений (центральная часть)
        self.messages_block = curses.newwin(self.max_y - 2, self.max_x, 1, 0)
        self.messages_block.scrollok(True)

        # Блок ввода (нижняя строка)
        self.input_block = curses.newwin(1, self.max_x, self.max_y - 1, 0)

        # Настройка keypad для блоков
        self.input_block.keypad(True)

    def resize_windows(self) -> None:
        """
        [RU]
        Пересоздание окон при изменении размера терминала.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Recreate windows when terminal size changes.
        
        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        self._create_windows()

    def get_status_window(self) -> curses.window:
        """
        [RU]
        Получение окна статуса.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            curses.window: Окно статуса

        [EN]
        Get status window.

        Returns:
            curses.window: Status window

        Args:
            None: Function does not accept arguments.

        Returns:
            curses.window: Status window
        """
        return self.status_block

    def get_messages_window(self) -> curses.window:
        """
        [RU]
        Получение окна сообщений.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            curses._CursesWindow: Окно сообщений

        [EN]
        Get messages window.

        Args:
            None: Function does not accept arguments.

        Returns:
            curses._CursesWindow: Messages window
        """
        return self.messages_block

    def get_input_window(self) -> curses.window:
        """
        [RU]
        Получение окна ввода.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            curses._CursesWindow: Окно ввода

        [EN]
        Get input window.

        Args:
            None: Function does not accept arguments.

        Returns:
            curses._CursesWindow: Input window
        """
        return self.input_block

    def get_available_messages_height(self) -> int:
        """
        [RU]
        Получение доступной высоты для сообщений.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            int: Доступная высота

        [EN]
        Get available height for messages.

        Args:
            None: Function does not accept arguments.

        Returns:
            int: Available height
        """
        return max(0, self.max_y - 3)

    def get_available_width(self) -> int:
        """
        [RU]
        Получение доступной ширины.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            int: Доступная ширина

        [EN]
        Get available width.

        Args:
            None: Function does not accept arguments.

        Returns:
            int: Available width
        """
        return self.max_x - 1

    def draw(self) -> None:
        """
        [RU]
        Отрисовка окон (пустая реализация для совместимости).

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Draw windows.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        pass

    def handle_input(self, key: int) -> bool:
        """
        [RU]
        Обработка ввода.

        Аргументы:
            key (int): Код клавиши

        Возвращает:
            bool: False

        [EN]
        Handle input.

        Args:
            key (int): Key code

        Returns:
            bool: False
        """
        return False
