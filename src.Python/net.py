#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для UDP сетевого взаимодействия
Module for UDP network communication
"""

import socket
import threading
from queue import Queue


class UdpSender:
    """
    Класс для отправки UDP сообщений на broadcast адрес
    Class for sending UDP messages to broadcast address
    """

    def __init__(self, ip: str, port: int):
        """
        Инициализация отправителя
        Initialize sender
        
        Args:
            ip (str): IP адрес интерфейса для привязки
            port (int): UDP порт для отправки
        """
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind((ip, 0))  # привязка к исходному интерфейсу со случайным портом
        self.broadcast_addr = ('255.255.255.255', port)

    def send(self, text: str) -> None:
        """
        Отправляет текстовое сообщение на broadcast адрес
        Sends text message to broadcast address
        
        Args:
            text (str): Текст сообщения для отправки
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
        Закрывает сокет
        Closes the socket
        """
        if hasattr(self, 'socket'):
            self.socket.close()


class UdpReceiverThread(threading.Thread):
    """
    Поток для приема UDP сообщений
    Thread for receiving UDP messages
    """

    def __init__(self, queue: Queue, ip: str, port: int):
        """
        Инициализация потока приемника
        Initialize receiver thread
        
        Args:
            queue (Queue): Очередь для сообщений
            ip (str): IP адрес для привязки
            port (int): UDP порт для приема
        """
        super().__init__(daemon=True)
        self.queue = queue
        self.ip = ip
        self.port = port
        self.running = True
        self.socket = None

    def run(self):
        """
        Основной цикл приема сообщений
        Main message receiving loop
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
        Останавливает поток приема
        Stops receiving thread
        """
        self.running = False
        if self.socket:
            self.socket.close()
