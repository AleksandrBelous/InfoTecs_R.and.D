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
            None: Конструктор не возвращает значение.

        [EN]
        Initialize input handler.

        Args:
            stdscr (curses.window): Curses window object.
            sender: UdpSender instance.
            renderer: UI renderer.

        Returns:
            None: Constructor does not return a value.
        """
        super().__init__(stdscr)
        self.sender = sender
        self.renderer = renderer

        # Состояние ввода
        self.nickname: str = ""
        self.input_buffer: str = ""
        self.input_mode: str = "nickname"  # "nickname" | "message"
        self.status: str = "Enter nickname"

    def get_nickname(self) -> str:
        """
        [RU]
        Получение текущего nickname.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            str: Текущий nickname

        [EN]
        Get current nickname.

        Args:
            None: Function does not accept arguments.

        Returns:
            str: Current nickname
        """
        return self.nickname

    def get_input_buffer(self) -> str:
        """
        [RU]
        Получение текущего буфера ввода.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            str: Текущий буфер ввода

        [EN]
        Get current input buffer.

        Args:
            None: Function does not accept arguments.

        Returns:
            str: Current input buffer
        """
        return self.input_buffer

    def get_input_mode(self) -> str:
        """
        [RU]
        Получение текущего режима ввода.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            str: Текущий режим ввода

        [EN]
        Get current input mode.

        Args:
            None: Function does not accept arguments.

        Returns:
            str: Current input mode
        """
        return self.input_mode

    def get_status(self) -> str:
        """
        [RU]
        Получение текущего статуса.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            str: Текущий статус

        [EN]
        Get current status.

        Args:
            None: Function does not accept arguments.

        Returns:
            str: Current status
        """
        return self.status

    def update_status(self, new_status: str) -> None:
        """
        [RU]
        Обновление статуса с автоматическим уведомлением рендерера.

        Аргументы:
            new_status (str): Новый текст статуса

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Update status with automatic renderer notification.

        Args:
            new_status (str): New status text

        Returns:
            None: Function does not return a value.
        """
        self.status = new_status
        self.renderer.set_status_dirty()

    def get_prompt(self) -> str:
        """
        [RU]
        Получение приглашения для ввода в зависимости от режима.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            str: Приглашение для ввода

        [EN]
        Get input prompt based on current mode.

        Args:
            None: Function does not accept arguments.

        Returns:
            str: Input prompt
        """
        return "nickname: " if self.input_mode == "nickname" else ">> "

    def _handle_nickname_mode(self) -> None:
        """
        [RU]
        Обработка ввода в режиме nickname.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Handle input in nickname mode.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        if self.input_buffer.strip():
            self.nickname = self.input_buffer.strip()
            self.input_mode = "message"
            self.input_buffer = ""
            self.update_status("Enter message")
        else:
            self.update_status("Nickname cannot be empty")
        self.renderer.set_input_dirty()

    def _handle_message_mode(self) -> None:
        """
        [RU]
        Обработка ввода в режиме сообщений.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Handle input in message mode.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        if self.input_buffer.strip():
            try:
                message = self.input_buffer.strip()
                self.sender.send_datagram(self.nickname, message)
                self.input_buffer = ""
                self.update_status("Message sent")
            except Exception as e:
                self.update_status(f"Error: {str(e)}")
        self.renderer.set_input_dirty()

    def _handle_enter_key(self) -> None:
        """
        [RU]
        Обработка клавиши Enter.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Handle Enter key.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        if self.input_mode == "nickname":
            self.update_status("Enter nickname")
            self._handle_nickname_mode()
        else:
            self._handle_message_mode()

    def _handle_backspace_key(self) -> None:
        """
        [RU]
        Обработка клавиши Backspace.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Handle Backspace key.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        if self.input_buffer:
            self.input_buffer = self.input_buffer[:-1]
            self.renderer.set_input_dirty()

    def _handle_printable_char(self, key: str) -> None:
        """
        [RU]
        Обработка печатаемых символов.

        Аргументы:
            key (str): Unicode символ

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Handle printable characters.

        Args:
            key (str): Unicode character

        Returns:
            None: Function does not return a value.
        """
        self.input_buffer += key
        self.renderer.set_input_dirty()

    def handle_input(self, key) -> bool:
        """
        [RU]
        Обработка пользовательского ввода.

        Аргументы:
            key: Unicode символ (str) или код клавиши (int)

        Возвращает:
            bool: True если ввод обработан, False иначе

        [EN]
        Handle user input.

        Args:
            key: Unicode character (str) or key code (int)

        Returns:
            bool: True if input was handled, False otherwise
        """
        if isinstance(key, str):
            # Проверяем на Enter как строку
            if key in ('\n', '\r'):
                self._handle_enter_key()
                return True
            # Unicode символ (кириллица, ASCII)
            self._handle_printable_char(key)
            return True
        elif isinstance(key, int):
            # Специальные клавиши (get_wch возвращает int только для спец.клавиш)
            if key in (10, 13, curses.KEY_ENTER):
                self._handle_enter_key()
                return True
            elif key in (127, 8, curses.KEY_BACKSPACE):
                self._handle_backspace_key()
                return True
        return False

    def draw(self) -> None:
        """
        [RU]
        Отрисовка компонента ввода.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция не возвращает значение.

        [EN]
        Draw input component.
        
        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        prompt = self.get_prompt()
        self.renderer.draw_input(prompt, self.input_buffer)
