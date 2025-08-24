#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[RU]
Обработчик пользовательского ввода.

[EN]
User input handler.
"""

import curses
from .base_ui import BaseUI


class InputHandler(BaseUI):
    """
    [RU]
    Обработчик пользовательского ввода с управлением режимами.

    [EN]
    User input handler with mode management.
    """

    def __init__(self, stdscr: curses.window, sender, renderer):
        """
        [RU]
        Инициализация обработчика ввода.

        Аргументы:
            stdscr (curses.window): Объект окна curses.
            sender: Экземпляр UdpSender.
            renderer: Рендерер UI.

        Возвращает:
            None

        [EN]
        Initialize input handler.

        Args:
            stdscr (curses.window): Curses window object.
            sender: UdpSender instance.
            renderer: UI renderer.

        Returns:
            None
        """
        super().__init__(stdscr)
        self.sender = sender
        self.renderer = renderer

        # Состояние ввода
        self.nickname: str = ""
        self.input_buffer: str = ""
        self.input_mode: str = "nickname"  # "nickname" | "message"
        self.status: str = "OK"

    def get_nickname(self) -> str:
        """
        [RU]
        Получение текущего nickname.

        Возвращает:
            str: Текущий nickname

        [EN]
        Get current nickname.

        Returns:
            str: Current nickname
        """
        return self.nickname

    def get_input_buffer(self) -> str:
        """
        [RU]
        Получение текущего буфера ввода.

        Возвращает:
            str: Текущий буфер ввода

        [EN]
        Get current input buffer.

        Returns:
            str: Current input buffer
        """
        return self.input_buffer

    def get_input_mode(self) -> str:
        """
        [RU]
        Получение текущего режима ввода.

        Возвращает:
            str: Текущий режим ввода

        [EN]
        Get current input mode.

        Returns:
            str: Current input mode
        """
        return self.input_mode

    def get_status(self) -> str:
        """
        [RU]
        Получение текущего статуса.

        Возвращает:
            str: Текущий статус

        [EN]
        Get current status.

        Returns:
            str: Current status
        """
        return self.status

    def get_prompt(self) -> str:
        """
        [RU]
        Получение приглашения для ввода в зависимости от режима.

        Возвращает:
            str: Приглашение для ввода

        [EN]
        Get input prompt based on current mode.

        Returns:
            str: Input prompt
        """
        return "nickname: " if self.input_mode == "nickname" else ">> "

    def _handle_nickname_mode(self) -> None:
        """
        [RU]
        Обработка ввода в режиме nickname.

        [EN]
        Handle input in nickname mode.
        """
        if self.input_buffer.strip():
            self.nickname = self.input_buffer.strip()
            self.input_mode = "message"
            self.input_buffer = ""
            self.status = "OK"
            self.renderer.set_status_dirty()
        else:
            self.status = "Nickname cannot be empty"
            self.renderer.set_status_dirty()
        self.renderer.set_input_dirty()

    def _handle_message_mode(self) -> None:
        """
        [RU]
        Обработка ввода в режиме сообщений.

        [EN]
        Handle input in message mode.
        """
        if self.input_buffer.strip():
            try:
                msg = f"{self.nickname}: {self.input_buffer.strip()}"
                self.sender.send_datagram(msg)
                self.input_buffer = ""
                self.status = "OK"
                self.renderer.set_status_dirty()
            except Exception as e:
                self.status = str(e)[:80]
                self.renderer.set_status_dirty()
        self.renderer.set_input_dirty()

    def _handle_enter_key(self) -> None:
        """
        [RU]
        Обработка клавиши Enter.

        [EN]
        Handle Enter key.
        """
        if self.input_mode == "nickname":
            self._handle_nickname_mode()
        else:
            self._handle_message_mode()

    def _handle_backspace_key(self) -> None:
        """
        [RU]
        Обработка клавиши Backspace.

        [EN]
        Handle Backspace key.
        """
        if self.input_buffer:
            self.input_buffer = self.input_buffer[:-1]
            self.renderer.set_input_dirty()

    def _handle_printable_char(self, key: int) -> None:
        """
        [RU]
        Обработка печатаемых символов.

        Аргументы:
            key (int): Код клавиши

        [EN]
        Handle printable characters.

        Args:
            key (int): Key code
        """
        self.input_buffer += chr(key)
        self.renderer.set_input_dirty()

    def handle_input(self, key: int) -> bool:
        """
        [RU]
        Обработка пользовательского ввода.

        Аргументы:
            key (int): Код клавиши

        Возвращает:
            bool: True если ввод обработан, False иначе

        [EN]
        Handle user input.

        Args:
            key (int): Key code

        Returns:
            bool: True if input was handled, False otherwise
        """
        if key in (10, 13, curses.KEY_ENTER):
            self._handle_enter_key()
            return True
        elif key in (127, 8, curses.KEY_BACKSPACE):
            self._handle_backspace_key()
            return True
        elif 32 <= key <= 126:
            self._handle_printable_char(key)
            return True
        return False

    def draw(self) -> None:
        """
        [RU]
        Отрисовка компонента ввода.

        [EN]
        Draw input component.
        """
        prompt = self.get_prompt()
        self.renderer.draw_input(prompt, self.input_buffer)
