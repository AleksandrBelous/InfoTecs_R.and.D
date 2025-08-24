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
            None

        [EN]
        Initialize window manager.

        Args:
            stdscr (curses.window): Curses window object.

        Returns:
            None
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

        [EN]
        Create/recreate interface windows.
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

        [EN]
        Recreate windows when terminal size changes.
        """
        self._create_windows()

    def get_status_window(self) -> curses.window:
        """
        [RU]
        Получение окна статуса.

        Возвращает:
            curses.window: Окно статуса

        [EN]
        Get status window.

        Returns:
            curses.window: Status window
        """
        return self.status_block

    def get_messages_window(self) -> curses.window:
        """
        [RU]
        Получение окна сообщений.

        Возвращает:
            curses._CursesWindow: Окно сообщений

        [EN]
        Get messages window.

        Returns:
            curses._CursesWindow: Messages window
        """
        return self.messages_block

    def get_input_window(self) -> curses.window:
        """
        [RU]
        Получение окна ввода.

        Возвращает:
            curses._CursesWindow: Окно ввода

        [EN]
        Get input window.

        Returns:
            curses._CursesWindow: Input window
        """
        return self.input_block

    def get_available_messages_height(self) -> int:
        """
        [RU]
        Получение доступной высоты для сообщений.

        Возвращает:
            int: Доступная высота

        [EN]
        Get available height for messages.

        Returns:
            int: Available height
        """
        return max(0, self.max_y - 3)

    def get_available_width(self) -> int:
        """
        [RU]
        Получение доступной ширины.

        Возвращает:
            int: Доступная ширина

        [EN]
        Get available width.

        Returns:
            int: Available width
        """
        return self.max_x - 1

    def draw(self) -> None:
        """
        [RU]
        Отрисовка окон (пустая реализация для совместимости).

        [EN]
        Draw windows (empty implementation for compatibility).
        """
        pass

    def handle_input(self, key: int) -> bool:
        """
        [RU]
        Обработка ввода (пустая реализация для совместимости).

        Аргументы:
            key (int): Код клавиши

        Возвращает:
            bool: False (не обрабатывает ввод)

        [EN]
        Handle input (empty implementation for compatibility).

        Args:
            key (int): Key code

        Returns:
            bool: False (does not handle input)
        """
        return False
