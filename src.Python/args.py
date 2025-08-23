#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для разбора аргументов командной строки
Module for parsing command line arguments
"""

import argparse
from argparse import Namespace


def parse_args() -> Namespace:
    """
    Разбирает аргументы командной строки
    Parses command line arguments
    
    Returns:
        Namespace: Объект с атрибутами ip (str) и port (int)
    """
    parser = argparse.ArgumentParser(
            description="IPv4 UDP broadcast chat",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Примеры использования / Usage examples:
  python3 main.py --ip 192.168.1.100 --port 12345
  python3 main.py --ip 10.0.0.5 --port 12345
        """
            )

    parser.add_argument(
            '--ip',
            type=str,
            required=True,
            help='IPv4 адрес интерфейса для приема сообщений'
            )

    parser.add_argument(
            '--port',
            type=int,
            required=True,
            help='UDP порт для приема и отправки сообщений'
            )

    return parser.parse_args()


if __name__ == "__main__":
    # Тестирование модуля
    try:
        args = parse_args()
        print(f"IP: {args.ip}")
        print(f"Port: {args.port}")
    except SystemExit:
        pass
