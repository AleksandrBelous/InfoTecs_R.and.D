#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[RU]
Модуль для UDP сетевого взаимодействия.

[EN]
Module for UDP network communication
"""

import socket
import threading
from queue import Queue


class UdpSender:
    """
    [RU]
    Класс для отправки UDP сообщений на broadcast адрес и порт.

    [EN]
    Class for sending UDP messages to broadcast address and port.
    """

    def __init__(self, ip: str, port: int):
        """
        [RU]
        Инициализация отправителя UDP сообщений.
        
        Аргументы:
            ip (str): IP адрес интерфейса для привязки.
            port (int): UDP порт для отправки.
            
        Возвращает:
            None: Конструктор не возвращает значение.
            
        [EN]
        Initialize UDP message sender.

        Args:
            ip (str): IP address of interface to bind.
            port (int): UDP port for sending.

        Returns:
            None: Constructor does not return a value.
        """
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind((ip, 0))  # привязка к исходному интерфейсу со случайным портом
        self.broadcast_addr = ('255.255.255.255', port)

    def send(self, text: str) -> None:
        """
        [RU]
        Отправляет текстовое сообщение на broadcast адрес.
        
        Аргументы:
            text (str): Текст сообщения для отправки.
            
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Sends text message to broadcast address.

        Args:
            text (str): Text message to send.

        Returns:
            None: Function does not return a value.
        """
        try:
            data = text.encode('utf-8')
            if len(data) > 1000:
                raise ValueError(f"Сообщение слишком длинное: {len(data)} байт (максимум 1000)")

            self.socket.sendto(data, self.broadcast_addr)
        except Exception as e:
            raise RuntimeError(f"Ошибка отправки: {e}")

    def close(self):
        """
        [RU]
        Закрывает сокет отправителя.
        
        Возвращает:
            None: Функция не возвращает значение.
            
        [EN]
        Closes the sender socket.

        Returns:
            None: Function does not return a value.
        """
        if hasattr(self, 'socket'):
            self.socket.close()


class UdpReceiverThread(threading.Thread):
    """
    [RU]
    Поток для приема UDP сообщений.
    
    [EN]
    Thread for receiving UDP messages.
    """

    def __init__(self, queue: Queue, ip: str, port: int):
        """
        [RU]
        Инициализация потока приемника UDP сообщений.
        
        Аргументы:
            queue (Queue): Очередь для сообщений.
            ip (str): IP адрес для привязки.
            port (int): UDP порт для приема.
            
        Возвращает:
            None: Конструктор не возвращает значение.
            
        [EN]
        Initialize UDP message receiver thread.

        Args:
            queue (Queue): Message queue.
            ip (str): IP address to bind.
            port (int): UDP port for receiving.

        Returns:
            None: Constructor does not return a value.
        """
        super().__init__(daemon=True)
        self.queue = queue
        self.ip = ip
        self.port = port
        self.running = True
        self.socket = None

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
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.socket.bind(("0.0.0.0", self.port))
            self.socket.settimeout(0.2)

            while self.running:
                try:
                    data, addr = self.socket.recvfrom(1024)
                    src_ip = addr[0]
                    try:
                        text = data.decode('utf-8', 'replace')
                        message = f"[{src_ip}] {text}"
                        self.queue.put(message)
                    except UnicodeDecodeError:
                        # Пропускаем некорректные сообщения
                        continue

                except socket.timeout:
                    # Таймаут - продолжаем цикл
                    continue
                except OSError:
                    # Сокет закрыт или другая ошибка
                    if self.running:
                        break
                    else:
                        break

        except Exception as e:
            error_msg = f"Ошибка приема: {e}"
            self.queue.put(error_msg)
        finally:
            if self.socket:
                self.socket.close()

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
        if self.socket:
            self.socket.close()
