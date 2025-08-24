#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[RU]
Модуль для UDP сетевого взаимодействия.

[EN]
Module for UDP network communication
"""

import json
import socket
import threading
from queue import Queue
from ui import CursesChatUI
from curses import wrapper


class UdpReceiverThread(threading.Thread):
    """
    [RU]
    Поток для приема UDP сообщений.
    
    [EN]
    Thread for receiving UDP messages.
    """

    def __init__(self, rx_queue: Queue, ip: str, port: int):
        """
        [RU]
        Инициализация потока приемника UDP сообщений.
        
        Аргументы:
            rx_queue (Queue): Очередь для сообщений.
            ip (str): IP адрес для идентификации подсети.
            port (int): UDP порт для прослушивания.
            
        Возвращает:
            None: Конструктор не возвращает значение.
            
        [EN]
        Initialize UDP message receiver thread.

        Args:
            rx_queue (Queue): Message queue.
            ip (str): IP address to identify subnet.
            port (int): UDP port for listening.

        Returns:
            None: Constructor does not return a value.
        """
        super().__init__(daemon=True)
        self.queue: Queue = rx_queue
        self.ip: str = ip
        self.port: int = port
        self.running: bool = True
        self.r_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        """
        [RU]
        Основной цикл приема сообщений.

        Аргументы:
            None: Функция не принимает аргументов.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Main message receiving loop.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        try:
            self.r_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.r_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.r_socket.bind(("0.0.0.0", self.port))
            self.r_socket.settimeout(0.2)

            while self.running:
                try:
                    data, addr = self.r_socket.recvfrom(2048)
                    src_ip = addr[0]
                    try:
                        text = data.decode('utf-8', 'replace')

                        # Очищаем текст от некорректных символов перед JSON парсингом
                        cleaned_text = text.encode('utf-8', 'replace').decode('utf-8')

                        # Пытаемся парсить как JSON
                        try:
                            json_data = json.loads(cleaned_text)
                            if isinstance(json_data, dict) and 'nickname' in json_data and 'message' in json_data:
                                nickname = json_data['nickname']
                                message = json_data['message']
                                formatted_message = f"[{src_ip}] {nickname}: {message}"
                            else:
                                # Некорректная JSON структура - показываем как есть
                                formatted_message = f"[{src_ip}] {cleaned_text}"
                        except json.JSONDecodeError:
                            # Не JSON - показываем как есть
                            formatted_message = f"[{src_ip}] {cleaned_text}"

                        self.queue.put(formatted_message)
                    except UnicodeDecodeError:
                        # Пропускаем некорректные сообщения
                        continue

                except socket.timeout:
                    # Таймаут - продолжаем цикл
                    continue
                except OSError:
                    # Сокет закрыт или другая ошибка
                    break

        except Exception as e:
            error_msg = f"Ошибка приема: {e}"
            self.queue.put(error_msg)
        finally:
            if self.r_socket:
                self.r_socket.close()

    def stop(self):
        """
        [RU]
        Останавливает поток приема сообщений.

        Аргументы:
            None: Функция не принимает аргументов.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Stops the message receiving thread.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        self.running = False
        if self.r_socket:
            self.r_socket.close()


class UdpSenderThread(threading.Thread):
    """
    [RU]
    Поток для ввода пользователя и отправки UDP сообщений.
    Объединяет функционал отправителя и UI в одном потоке.
    
    [EN]
    Thread for user input and UDP message sending.
    Combines sender functionality and UI in one thread.
    """

    def __init__(self, rx_queue: Queue, ip: str, port: int):
        """
        [RU]
        Инициализация потока отправки UDP сообщений.
        
        Аргументы:
            rx_queue (Queue): Очередь входящих сообщений.
            ip (str): IP адрес интерфейса для привязки.
            port (int): UDP порт для отправки.
            
        Возвращает:
            None: Конструктор не возвращает значение.
            
        [EN]
        Initialize UDP message sending thread.

        Args:
            rx_queue (Queue): Incoming message queue.
            ip (str): IP address of interface to bind.
            port (int): UDP port for sending.

        Returns:
            None: Constructor does not return a value.
        """
        super().__init__(daemon=True)
        self.rx_queue: Queue = rx_queue
        self.ip: str = ip
        self.port: int = port
        self.running: bool = True

        # Создаем сокет для отправки
        self.s_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.s_socket.bind((ip, 0))  # привязка к указанному интерфейсу со случайным портом
        self.broadcast_addr = ('255.255.255.255', port)

    def send_datagram(self, nickname: str, message: str) -> None:
        """
        [RU]
        Отправляет сообщение с nickname в JSON формате на broadcast адрес и порт.
        
        Аргументы:
            nickname (str): Имя пользователя.
            message (str): Текст сообщения для отправки.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Sends message with nickname in JSON format to broadcast address and port.

        Args:
            nickname (str): User nickname.
            message (str): Text message to send.

        Returns:
            None: Function does not return a value.
        """
        try:
            # Проверяем message на объем не более 1000 байт
            message_bytes = message.encode('utf-8')
            if len(message_bytes) > 1000:
                raise ValueError(f"Сообщение слишком длинное: {len(message_bytes)} байт (максимум 1000)")

            # Формируем JSON структуру
            json_data = {
                    "nickname": nickname,
                    "message" : message
                    }

            # Упаковываем в JSON и отправляем
            data = json.dumps(json_data, ensure_ascii=False).encode('utf-8')
            self.s_socket.sendto(data, self.broadcast_addr)
        except Exception as e:
            raise RuntimeError(f"Ошибка отправки: {e}")

    def _ui_entry(self, stdscr, rx_queue, ip, port):
        """
        [RU]
        Точка входа для curses wrapper.
        
        Аргументы:
            stdscr: Объект окна curses.
            rx_queue (Queue): Очередь входящих сообщений.
            ip (str): IP адрес интерфейса.
            port (int): UDP порт.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Entry point for curses wrapper.

        Args:
            stdscr: Curses window object.
            rx_queue (Queue): Incoming message queue.
            ip (str): Interface IP address.
            port (int): UDP port.

        Returns:
            None: Function does not return a value.
        """
        ui = CursesChatUI(stdscr, self, rx_queue, ip, port)  # self вместо sender
        ui.run()

    def run(self):
        """
        [RU]
        Основной цикл потока: запуск UI через curses wrapper.
        
        Аргументы:
            None: Функция не принимает аргументов.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Main thread loop: launch UI through curses wrapper.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        try:
            wrapper(self._ui_entry, self.rx_queue, self.ip, self.port)
        except Exception as e:
            print(f"Ошибка UI потока: {e}")

    def close_socket(self):
        """
        [RU]
        Закрывает сокет отправителя.
        
        Аргументы:
            None: Функция не принимает аргументов.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Closes the sender socket.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        if self.s_socket:
            self.s_socket.close()

    def stop(self):
        """
        [RU]
        Останавливает поток отправки.
        
        Аргументы:
            None: Функция не принимает аргументов.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Stops the sending thread.

        Args:
            None: Function does not accept arguments.

        Returns:
            None: Function does not return a value.
        """
        self.running = False
        self.close_socket()
