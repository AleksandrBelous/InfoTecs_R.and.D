#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для разбора аргументов командной строки
Module for parsing command line arguments
"""

import argparse
import socket
import ipaddress
import subprocess
from argparse import Namespace


def is_ip_valid(ip: str) -> bool:
    """
    Проверяет существование IP адреса на текущей машине
    Validates if IP address exists on current machine
    
    Args:
        ip (str): IP адрес для проверки
        
    Returns:
        bool: True если IP адрес существует, False иначе
    """
    try:
        # Проверяем корректность формата IPv4
        ipaddress.IPv4Address(ip)

        # Проверяем через ip addr show (работает на всех Linux)
        try:
            result = subprocess.run(
                    ['ip', 'addr', 'show'],
                    capture_output=True,
                    text=True,
                    timeout=3
                    )
            if result.returncode == 0 and ip in result.stdout:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Fallback: проверяем возможность привязки к указанному IP адресу
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            test_socket.bind((ip, 0))
            return True
        except OSError:
            return False
        finally:
            test_socket.close()

    except (ipaddress.AddressValueError, socket.gaierror, OSError):
        return False


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

    args = parser.parse_args()

    # Валидация IP адреса
    if not is_ip_valid(args.ip):
        parser.error(f"Ошибка: IP адрес '{args.ip}' не существует на текущей машине или имеет неверный формат")

    return args


if __name__ == "__main__":
    # Тестирование модуля
    try:
        args = parse_args()
        print(f"IP: {args.ip}")
        print(f"Port: {args.port}")
    except SystemExit:
        pass
