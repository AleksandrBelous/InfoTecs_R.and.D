#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[RU]
Рендерер для отрисовки UI компонентов.

[EN]
Renderer for UI component drawing.
"""

import curses
from .base_ui import BaseUI


class UIRenderer(BaseUI):
    """
    [RU]
    Рендерер для отрисовки UI компонентов (статус, ввод).

    [EN]
    Renderer for UI component drawing (status, input).
    """

    def __init__(self, stdscr: curses.window, window_manager):
        """
        [RU]
        Инициализация рендерера.

        Аргументы:
            stdscr (curses.window): Объект окна curses.
            window_manager: Менеджер окон.

        Возвращает:
            None

        [EN]
        Initialize renderer.

        Args:
            stdscr (curses.window): Curses window object.
            window_manager: Window manager.

        Returns:
            None
        """
        super().__init__(stdscr)
        self.window_manager = window_manager

        # Dirty flags для оптимизации отрисовки
        self._dirty_status: bool = True
        self._dirty_input: bool = True

    def set_status_dirty(self) -> None:
        """
        [RU]
        Установка флага необходимости перерисовки статуса.

        [EN]
        Set flag for status redraw requirement.
        """
        self._dirty_status = True

    def set_input_dirty(self) -> None:
        """
        [RU]
        Установка флага необходимости перерисовки ввода.

        [EN]
        Set flag for input redraw requirement.
        """
        self._dirty_input = True

    def set_all_dirty(self) -> None:
        """
        [RU]
        Установка флагов необходимости перерисовки всех компонентов.

        [EN]
        Set flags for all components redraw requirement.
        """
        self._dirty_status = True
        self._dirty_input = True

    def draw_status(self, status_text: str) -> None:
        """
        [RU]
        Отрисовка статусной строки.

        Аргументы:
            status_text (str): Текст статуса

        [EN]
        Draw status line.

        Args:
            status_text (str): Status text
        """
        if not self._dirty_status:
            return

        status_window = self.window_manager.get_status_window()
        max_width = self.window_manager.get_available_width()

        status_window.clear()
        try:
            status_window.addstr(0, 0, status_text[:max_width])
        except curses.error:
            pass
        status_window.refresh()
        self._dirty_status = False

    def draw_input(self, prompt: str, input_buffer: str) -> None:
        """
        [RU]
        Отрисовка поля ввода.

        Аргументы:
            prompt (str): Приглашение для ввода
            input_buffer (str): Текущий буфер ввода

        [EN]
        Draw input field.

        Args:
            prompt (str): Input prompt
            input_buffer (str): Current input buffer
        """
        if not self._dirty_input:
            return

        input_window = self.window_manager.get_input_window()
        max_width = self.window_manager.get_available_width()

        input_window.clear()
        line = (prompt + input_buffer)[:max_width]
        try:
            input_window.addstr(0, 0, line)
        except curses.error:
            pass
        try:
            input_window.move(0, min(len(line), max_width))
        except curses.error:
            pass
        input_window.refresh()
        self._dirty_input = False

    def focus_input_caret(self, prompt: str, input_buffer: str) -> None:
        """
        [RU]
        Установка курсора в поле ввода без перерисовки.

        Аргументы:
            prompt (str): Приглашение для ввода
            input_buffer (str): Текущий буфер ввода

        [EN]
        Set cursor in input field without redrawing.

        Args:
            prompt (str): Input prompt
            input_buffer (str): Current input buffer
        """
        input_window = self.window_manager.get_input_window()
        max_width = self.window_manager.get_available_width()
        line_len = min(len(prompt + input_buffer), max_width)
        try:
            input_window.move(0, line_len)
            input_window.refresh()
        except curses.error:
            pass

    def draw(self) -> None:
        """
        [RU]
        Отрисовка всех компонентов (пустая реализация).

        [EN]
        Draw all components (empty implementation).
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
