#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[RU]
Отображение сообщений в UI.

[EN]
Message display in UI.
"""

import curses
import textwrap
from typing import List
from .base_ui import BaseUI


class MessageDisplay(BaseUI):
    """
    [RU]
    Компонент отображения сообщений.

    [EN]
    Message display component.
    """

    def __init__(self, stdscr: curses.window, window_manager, renderer):
        """
        [RU]
        Инициализация компонента отображения сообщений.

        Аргументы:
            stdscr (curses.window): Объект окна curses.
            window_manager: Менеджер окон.
            renderer: Рендерер UI.

        Возвращает:
            None: Конструктор не возвращает значение.

        [EN]
        Initialize message display component.

        Args:
            stdscr (curses.window): Curses window object.
            window_manager: Window manager.
            renderer: UI renderer.

        Returns:
            None: Constructor does not return a value.
        """
        super().__init__(stdscr)
        self.window_manager = window_manager
        self.renderer = renderer

        # Состояние сообщений
        self.messages: List[str] = []
        self._last_messages_len: int = 0
        self._dirty_messages: bool = True
        self._full_redraw_pending: bool = True

    def add_message(self, message: str) -> None:
        """
        [RU]
        Добавление нового сообщения в историю.

        Аргументы:
            message (str): Новое сообщение

        [EN]
        Add new message to history.

        Args:
            message (str): New message

        Returns:
            None: Function does not return a value.
        """
        self.messages.append(message)

        # Ограничиваем историю
        if len(self.messages) > 500:
            self.messages = self.messages[-500:]

        self._dirty_messages = True

    def get_messages(self) -> List[str]:
        """
        [RU]
        Получение списка сообщений.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            List[str]: Список сообщений

        [EN]
        Get messages list.

        Args:
            None: Function does not accept arguments.

        Returns:
            List[str]: Messages list
        """
        return self.messages.copy()

    def clear_messages(self) -> None:
        """
        [RU]
        Очистка истории сообщений.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Clear message history.
        
        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        self.messages.clear()
        self._last_messages_len = 0
        self._dirty_messages = True
        self._full_redraw_pending = True

    def set_dirty(self) -> None:
        """
        [RU]
        Установка флага необходимости перерисовки.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Set dirty flag for redraw requirement.
        
        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        self._dirty_messages = True

    def set_full_redraw_pending(self) -> None:
        """
        [RU]
        Установка флага необходимости полной перерисовки.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Set full redraw pending flag.
        
        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        self._full_redraw_pending = True

    def _wrap_message(self, msg: str, max_width: int) -> List[str]:
        """
        [RU]
        Перенос строки сообщения.

        Аргументы:
            msg (str): Сообщение для переноса
            max_width (int): Максимальная ширина

        Возвращает:
            List[str]: Список строк после переноса

        [EN]
        Word wrap message.

        Args:
            msg (str): Message to wrap
            max_width (int): Maximum width

        Returns:
            List[str]: List of wrapped lines
        """
        if max_width <= 1 or len(msg) <= max_width:
            return [msg]

        return textwrap.wrap(
                msg,
                width=max_width,
                break_long_words=True,
                break_on_hyphens=False
                )

    def _draw_messages_full(self) -> None:
        """
        [RU]
        Полная отрисовка блока сообщений.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Full redraw of messages block.
        
        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        messages_window = self.window_manager.get_messages_window()
        max_lines = self.window_manager.get_available_messages_height()
        max_width = self.window_manager.get_available_width()

        messages_window.clear()

        wrapped_all: List[str] = []
        for msg in self.messages:
            wrapped_all.extend(self._wrap_message(msg, max_width=max_width))

        tail = wrapped_all[-max_lines:] if max_lines > 0 else []
        for i, line in enumerate(tail):
            if i >= max_lines:
                break
            try:
                messages_window.addstr(i, 0, line[:max_width])
            except curses.error:
                pass

        # Курсор в конце блока сообщений
        try:
            messages_window.move(min(len(tail), max_lines - 1), 0)
        except curses.error:
            pass

        messages_window.refresh()
        self._last_messages_len = len(self.messages)
        self._dirty_messages = False

    def _append_new_messages(self) -> None:
        """
        [RU]
        Добавление только новых сообщений.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Append only new messages.
        
        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        if self._last_messages_len > len(self.messages):
            # История была усечена — нужен полный redraw
            self._full_redraw_pending = True
            return

        if self._last_messages_len == len(self.messages):
            self._dirty_messages = False
            return

        messages_window = self.window_manager.get_messages_window()
        max_width = self.window_manager.get_available_width()

        try:
            for msg in self.messages[self._last_messages_len:]:
                for line in self._wrap_message(msg, max_width=max_width):
                    try:
                        # Добавляем строку и перенос
                        messages_window.addstr(line[:max_width] + "\n")
                    except curses.error:
                        pass
            messages_window.refresh()
        finally:
            self._last_messages_len = len(self.messages)
            self._dirty_messages = False

        # Возвращаем курсор в поле ввода
        self.renderer.focus_input_caret("", "")

    def draw(self) -> None:
        """
        [RU]
        Отрисовка блока сообщений.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Draw messages block.
        
        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        if self._full_redraw_pending:
            self._draw_messages_full()
            self._full_redraw_pending = False
        elif self._dirty_messages:
            self._append_new_messages()

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
