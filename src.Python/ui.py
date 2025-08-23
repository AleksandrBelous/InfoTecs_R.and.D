#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[RU]
Модуль пользовательского интерфейса на основе curses.

[EN]
Module for curses-based user interface
"""

import curses
from queue import Queue
from typing import List


class CursesChatUI:
    """
    [RU]
    Пользовательский интерфейс чата на основе curses.

    [EN]
    Curses-based chat user interface
    """

    def __init__(self, stdscr, sender, rx_queue: Queue, iface_ip: str, port: int):
        """
        [RU]
        Инициализация UI.
        
        Аргументы:
            stdscr: Объект окна curses.
            sender: Экземпляр UdpSender.
            rx_queue (Queue): Очередь входящих сообщений.
            iface_ip (str): IP адрес интерфейса.
            port (int): UDP порт.
            
        Возвращает:
            None: Конструктор не возвращает значение.
            
        [EN]
        Initialize UI.
        
        Args:
            stdscr: Curses window object.
            sender: UdpSender instance.
            rx_queue (Queue): Message queue.
            iface_ip (str): Interface IP address.
            port (int): UDP port.

        Returns:
            None: Constructor does not return a value.
        """
        self.stdscr = stdscr
        self.sender = sender
        self.rx_queue: Queue = rx_queue
        self.iface_ip: str = iface_ip
        self.port: int = port

        # Состояние UI
        self.nickname: str = ""
        self.messages: List[str] = []
        self.input_buffer: str = ""
        self.input_mode: str = "nickname"  # "nickname" или "message"
        self.status: str = "OK"

        # Настройка curses
        curses.curs_set(1)  # Показывать курсор
        curses.noecho()  # Не эхо ввода
        curses.cbreak()  # Немедленная обработка клавиш

        # Атрибуты для работы с экраном
        self.max_y: int = 0
        self.max_x: int = 0
        self.status_block = None
        self.messages_block = None
        self.input_block = None

    def _create_windows(self):
        """
        [RU]
        Создает окна для разных панелей.

        Аргументы:
            None: Функция не принимает аргументов.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Creates windows for different panels.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        self.max_y, self.max_x = self.stdscr.getmaxyx()

        # Статусная панель (верхняя строка)
        self.status_block = curses.newwin(1, self.max_x, 0, 0)

        # Панель сообщений (основная область)
        self.messages_block = curses.newwin(self.max_y - 2, self.max_x, 1, 0)
        self.messages_block.scrollok(True)

        # Панель ввода (нижняя строка)
        self.input_block = curses.newwin(1, self.max_x, self.max_y - 1, 0)

        # Включить keypad режим для лучшей обработки клавиш
        self.stdscr.keypad(True)
        self.input_block.keypad(True)

    def _draw_status(self):
        """
        [RU]
        Отрисовывает статусную панель.

        Аргументы:
            None: Функция не принимает аргументов.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Draws the status panel.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        self.status_block.clear()
        status_line = f"iface={self.iface_ip}:{self.port} | nickname={self.nickname or '---'} | status={self.status}"
        self.status_block.addstr(0, 0, status_line[:self.max_x - 1])
        self.status_block.refresh()

    def _draw_messages(self):
        """
        [RU]
        Отрисовывает панель сообщений.

        Аргументы:
            None: Функция не принимает аргументов.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Draws the messages panel.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        self.messages_block.clear()

        # Показываем последние сообщения (с учетом размера экрана)
        max_lines = self.max_y - 3
        start_idx = max(0, len(self.messages) - max_lines)

        for i, msg in enumerate(self.messages[start_idx:]):
            if i >= max_lines:
                break
            # Обрезаем сообщение если оно слишком длинное
            display_msg = msg[:self.max_x - 1]
            self.messages_block.addstr(i, 0, display_msg)

        self.messages_block.refresh()

    def _draw_input(self):
        """
        [RU]
        Отрисовывает панель ввода.
        
        Аргументы:
            None: Функция не принимает аргументов.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Draws the input panel.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        self.input_block.clear()

        if self.input_mode == "nickname":
            prompt = "nickname: "
        else:
            prompt = ">> "

        # Показываем приглашение и буфер ввода
        input_line = prompt + self.input_buffer
        display_line = input_line[:self.max_x - 1]
        self.input_block.addstr(0, 0, display_line)

        # Позиционируем курсор
        cursor_pos = len(prompt) + len(self.input_buffer)
        if cursor_pos < self.max_x:
            self.input_block.move(0, cursor_pos)

        self.input_block.refresh()

    def _process_input(self, key):
        """
        [RU]
        Обрабатывает ввод пользователя.
        
        Аргументы:
            key (int): Код нажатой клавиши.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Processes user input.
        
        Args:
            key (int): Key code of pressed key.

        Returns:
            None: Function does not return a value.
        """
        if key in (10, 13, curses.KEY_ENTER):  # Enter (разные коды для разных терминалов)
            if self.input_mode == "nickname":
                if self.input_buffer.strip():
                    self.nickname = self.input_buffer.strip()
                    self.input_mode = "message"
                    self.input_buffer = ""
                    self.status = "OK"
            else:  # message mode
                if self.input_buffer.strip():
                    try:
                        message = f"{self.nickname}: {self.input_buffer.strip()}"
                        self.sender.send(message)
                        self.input_buffer = ""
                        self.status = "OK"
                    except Exception as e:
                        self.status = str(e)[:20]  # Обрезаем длинные ошибки
        elif key in (127, 8, curses.KEY_BACKSPACE):  # Backspace (разные коды для разных терминалов)
            if self.input_buffer:
                self.input_buffer = self.input_buffer[:-1]
        elif 32 <= key <= 126:  # Печатаемые символы
            self.input_buffer += chr(key)

    def _check_messages(self):
        """
        [RU]
        Проверяет новые сообщения в очереди.
        
        Аргументы:
            None: Функция не принимает аргументов.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Checks for new messages in the queue.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        while not self.rx_queue.empty():
            try:
                msg = self.rx_queue.get_nowait()
                self.messages.append(msg)
                # Ограничиваем количество сообщений в памяти
                if len(self.messages) > 500:
                    self.messages = self.messages[-500:]
            except:
                break

    def run(self):
        """
        [RU]
        Основной цикл UI.
        
        Аргументы:
            None: Функция не принимает аргументов.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Main UI loop.
        
        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        try:
            while True:
                # Обновляем размеры при изменении размера терминала
                new_max_y, new_max_x = self.stdscr.getmaxyx()
                if new_max_y != self.max_y or new_max_x != self.max_x:
                    self.max_y, self.max_x = new_max_y, new_max_x
                    self._create_windows()

                # Проверяем новые сообщения
                self._check_messages()

                # Отрисовываем все панели
                self._draw_status()
                self._draw_messages()
                self._draw_input()

                # Обрабатываем ввод (неблокирующий)
                self.stdscr.timeout(100)  # Таймаут 100мс
                try:
                    key = self.stdscr.getch()
                    if key != -1:  # -1 означает таймаут
                        self._process_input(key)
                except KeyboardInterrupt:
                    break

        except KeyboardInterrupt:
            pass
        finally:
            # Восстанавливаем терминал
            curses.nocbreak()
            curses.echo()
            curses.curs_set(1)
