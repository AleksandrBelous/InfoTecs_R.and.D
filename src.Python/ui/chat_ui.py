#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[RU]
Основной класс пользовательского интерфейса чата.

[EN]
Main chat user interface class.
"""

import curses
from queue import Queue, Empty

from .input_handler import InputHandler
from .message_display import MessageDisplay
from .renderer import UIRenderer
from .window_manager import WindowManager


class CursesChatUI:
    """
    [RU]
    Пользовательский интерфейс чата на основе curses с композицией компонентов.

    [EN]
    Curses-based chat user interface with component composition.
    """

    def __init__(self, stdscr, sender, rx_queue: Queue, iface_ip: str, port: int):
        """
        [RU]
        Инициализация UI чата.

        Аргументы:
            stdscr: Объект окна curses.
            sender: Экземпляр UdpSender.
            rx_queue (Queue): Очередь входящих сообщений.
            iface_ip (str): IP адрес интерфейса.
            port (int): UDP порт.

        Возвращает:
            None

        [EN]
        Initialize chat UI.

        Args:
            stdscr: Curses window object.
            sender: UdpSender instance.
            rx_queue (Queue): Incoming message queue.
            iface_ip (str): Interface IP address.
            port (int): UDP port.

        Returns:
            None
        """
        self.stdscr: curses.window = stdscr
        self.sender = sender
        self.rx_queue: Queue = rx_queue
        self.iface_ip: str = iface_ip
        self.port: int = port

        # Создание компонентов UI
        self.window_manager = WindowManager(stdscr)
        self.renderer = UIRenderer(stdscr, self.window_manager)
        self.input_handler = InputHandler(stdscr, sender, self.renderer)
        self.message_display = MessageDisplay(stdscr, self.window_manager, self.renderer)

        # Состояние UI
        self._full_redraw_pending: bool = True

    def _create_windows(self) -> None:
        """
        [RU]
        Создание/пересоздание окон через менеджер окон.

        [EN]
        Create/recreate windows through window manager.
        """
        self.window_manager.resize_windows()
        self._full_redraw_pending = True
        self.renderer.set_all_dirty()
        self.message_display.set_full_redraw_pending()

    def _initial_paint(self) -> None:
        """
        [RU]
        Единоразовый принудительный показ экрана при старте.

        [EN]
        One-time forced paint on startup.
        """
        try:
            self.stdscr.clear()
            self.stdscr.refresh()
        except curses.error:
            pass

        # Полный цикл первичной отрисовки
        self._draw_all_components()
        self._focus_input_caret()

    def _draw_all_components(self) -> None:
        """
        [RU]
        Отрисовка всех компонентов UI.

        [EN]
        Draw all UI components.
        """
        # Отрисовка статуса
        status_text = f"iface={self.iface_ip}:{self.port} | nickname={self.input_handler.get_nickname() or '---'} | status={self.input_handler.get_status()}"
        self.renderer.draw_status(status_text)

        # Отрисовка сообщений
        self.message_display.draw()

        # Отрисовка ввода
        self.input_handler.draw()

    def _focus_input_caret(self) -> None:
        """
        [RU]
        Фокусировка курсора в поле ввода.

        [EN]
        Focus cursor in input field.
        """
        prompt = self.input_handler.get_prompt()
        input_buffer = self.input_handler.get_input_buffer()
        self.renderer.focus_input_caret(prompt, input_buffer)

    def _check_messages(self) -> None:
        """
        [RU]
        Забирает новые сообщения из очереди.

        [EN]
        Drain incoming messages from queue.
        """
        drained = 0
        while True:
            try:
                msg = self.rx_queue.get_nowait()
            except Empty:
                break
            else:
                self.message_display.add_message(msg)
                drained += 1

    def run(self) -> None:
        """
        [RU]
        Основной цикл UI.

        [EN]
        Main UI loop.
        """
        try:
            # Явно очистим и «покажем» базовый экран
            try:
                self.stdscr.clear()
                self.stdscr.refresh()
            except curses.error:
                pass

            # Первичный принудительный показ
            self._initial_paint()
            self._full_redraw_pending = False

            # Неблокирующее ожидание клавиш
            self.stdscr.timeout(200)

            while True:
                # Проверка изменения размера терминала
                if self.window_manager.update_terminal_size():
                    self._create_windows()
                    # Полная перерисовка и возврат курсора в инпут
                    self._draw_all_components()
                    self._focus_input_caret()
                    self._full_redraw_pending = False

                # Входящие сообщения
                self._check_messages()

                # Перерисовки только при необходимости
                if self._full_redraw_pending:
                    self._draw_all_components()
                    self._focus_input_caret()
                    self._full_redraw_pending = False
                else:
                    # Отрисовка компонентов с проверкой dirty flags
                    self.message_display.draw()
                    self.renderer.draw_status(
                            f"iface={self.iface_ip}:{self.port} | nickname={self.input_handler.get_nickname() or '---'} | status={self.input_handler.get_status()}"
                            )
                    self.input_handler.draw()

                    # Фокусировка курсора после отрисовки
                    self._focus_input_caret()

                # Обработка ввода
                try:
                    key = self.stdscr.getch()
                    if key != -1:
                        self.input_handler.handle_input(key)
                except KeyboardInterrupt:
                    break

        except KeyboardInterrupt:
            pass
        finally:
            # Восстановление терминала
            self.window_manager.cleanup()
