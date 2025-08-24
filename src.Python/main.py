#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[RU]
Главный модуль UDP чата.

[EN]
Main UDP chat module.
"""

import sys
import locale
from queue import Queue
import time
from args import parse_args
from net import UdpReceiverThread, UdpSenderThread


def main():
    """
    [RU]
    Главная функция приложения с двумя потоками.
    
    Аргументы:
        None: Функция не принимает аргументов.
        
    Возвращает:
        None: Функция не возвращает значение.
        
    [EN]
    Main application function with two threads.
    
    Args:
        None: Function does not accept arguments.
        
    Returns:
        None: Function does not return a value.
    """
    rx_thread, tx_thread = None, None

    try:
        # Настройка локализации для поддержки кириллицы
        locale.setlocale(locale.LC_ALL, '')

        # Разбор аргументов командной строки
        args = parse_args()

        # Создание очереди для сообщений
        rx_queue = Queue()

        # Создание потоков
        rx_thread = UdpReceiverThread(rx_queue, args.ip, args.port)
        tx_thread = UdpSenderThread(rx_queue, args.ip, args.port)

        # Запуск потоков
        rx_thread.start()
        tx_thread.start()

        print(f"Запуск чата на {args.ip}:{args.port}")
        print("Нажмите Ctrl+C для выхода")

        # Ожидание завершения потоков
        while rx_thread.is_alive() or tx_thread.is_alive():
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nПолучен сигнал прерывания. Завершение...")

        # Завершение потоков
        if 'rx_thread' in locals():
            rx_thread.stop()
        if 'tx_thread' in locals():
            tx_thread.stop()

        # Ждем завершения с таймаутом
        if 'rx_thread' in locals():
            rx_thread.join(timeout=2)
        if 'tx_thread' in locals():
            tx_thread.join(timeout=2)

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    finally:
        # Дополнительная очистка
        try:
            if 'rx_thread' in locals() and rx_thread.is_alive():
                rx_thread.stop()
                rx_thread.join(timeout=1)
            if 'tx_thread' in locals() and tx_thread.is_alive():
                tx_thread.stop()
                tx_thread.join(timeout=1)
        except:
            pass
        print("Чат завершен.")


if __name__ == "__main__":
    main()
