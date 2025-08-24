#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[RU]
Модуль для разбора аргументов командной строки.

[EN]
Module for parsing command line arguments.
"""

import argparse
import socket
import ipaddress
import subprocess
from argparse import Namespace


def is_ip_valid(ip: str) -> tuple[bool, str]:
    """
    [RU]
    Проверяет валидность IP адреса и возвращает сообщение об ошибке.
    
    Аргументы:
        ip (str): IP адрес для проверки.
        
    Возвращает:
        tuple[bool, str]: (валидность, сообщение об ошибке).
        
    [EN]
    Validates IP address and returns error message.
    
    Args:
        ip (str): IP address to validate.
        
    Returns:
        tuple[bool, str]: (validity, error message).
    """
    # Проверка 1: Корректность формата IPv4
    try:
        ipaddress.IPv4Address(ip)
    except ipaddress.AddressValueError:
        return False, f"Некорректный формат IP адреса: '{ip}'. Ожидается IPv4 адрес в формате X.X.X.X"

    # Проверка 2: Существование IP адреса на машине через ip addr show
    try:
        result = subprocess.run(
                ['ip', 'addr', 'show'],
                capture_output=True,
                text=True,
                timeout=3
                )
        if result.returncode == 0 and ip in result.stdout:
            # IP найден в интерфейсах, проверяем возможность привязки
            pass
        else:
            return False, f"IP адрес '{ip}' не найден на текущей машине."
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Если команда ip недоступна, переходим к проверке сокета
        pass

    # Проверка 3: Возможность привязки к сокету
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        test_socket.bind((ip, 0))
        test_socket.close()
        return True, "IP адрес валиден"
    except OSError as e:
        test_socket.close()
        return False, f"Невозможно привязать сокет к IP адресу '{ip}': {str(e)}"


def parse_args() -> Namespace:
    """
    [RU]
    Разбирает аргументы командной строки.

    Аргументы:
        None: Функция не принимает аргументов.
    
    Возвращает:
        Namespace: Объект с атрибутами ip (str) и port (int).
        
    [EN]
    Parses command line arguments.
    
    Args:
        None: Function does not accept arguments.
        
    Returns:
        Namespace: Object with attributes ip (str) and port (int).
    """
    parser = argparse.ArgumentParser(
            description="IPv4 UDP broadcast chat",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Примеры использования / Usage examples:
  python3 main.py --ip 192.168.56.10 --port 12345
        """
            )

    parser.add_argument(
            '--ip',
            type=str,
            required=True,
            help='IPv4 адрес интерфейса для идентификации подсети'
            )

    parser.add_argument(
            '--port',
            type=int,
            required=True,
            help='UDP порт для приема и отправки сообщений'
            )

    args = parser.parse_args()

    # Валидация IP адреса с сообщением об ошибке
    is_valid_ip, error_message = is_ip_valid(args.ip)
    if not is_valid_ip:
        parser.error(error_message)

    return args


if __name__ == "__main__":
    # Тестирование модуля
    try:
        args = parse_args()
        print(f"IP: {args.ip}")
        print(f"Port: {args.port}")
    except SystemExit:
        pass
