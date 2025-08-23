#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный модуль UDP чата
Main UDP chat module
"""

import sys
import signal
from queue import Queue
from curses import wrapper

from args import parse_args
from net import UdpSender, UdpReceiverThread
from ui import CursesChatUI


def signal_handler(signum, frame):
    """
    Обработчик сигналов для корректного завершения
    Signal handler for graceful shutdown
    """
    print("\nПолучен сигнал завершения. Выход...")
    sys.exit(0)


def ui_entry(stdscr, sender, rx_queue, ip, port):
    """
    Точка входа для curses wrapper
    Entry point for curses wrapper
    
    Args:
        stdscr: Curses window object
        sender: UdpSender instance
        rx_queue (Queue): Очередь сообщений
        ip (str): IP адрес интерфейса
        port (int): UDP порт
    """
    ui = CursesChatUI(stdscr, sender, rx_queue, ip, port)
    ui.run()


def main():
    """
    Главная функция приложения
    Main application function
    """
    # Настройка обработчиков сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Разбор аргументов командной строки
        args = parse_args()

        # Создание очереди для сообщений
        rx_queue = Queue()

        # Создание сетевых компонентов
        rx_thread = UdpReceiverThread(rx_queue, args.ip, args.port)
        tx_sender = UdpSender(args.ip, args.port)

        # Запуск потока приема
        rx_thread.start()

        print(f"Запуск чата на {args.ip}:{args.port}")
        print("Нажмите Ctrl+C для выхода")

        # Запуск UI через curses wrapper
        wrapper(ui_entry, tx_sender, rx_queue, args.ip, args.port)

    except KeyboardInterrupt:
        print("\nПолучен сигнал прерывания. Завершение...")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    finally:
        # Корректное завершение
        try:
            if 'rx_thread' in locals():
                rx_thread.stop()
                rx_thread.join(timeout=1)
            if 'tx_sender' in locals():
                tx_sender.close()
        except:
            pass
        print("Чат завершен.")


if __name__ == "__main__":
    main()
