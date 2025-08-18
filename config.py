"""
Конфигурация IPv4-чата
Configuration for IPv4 Chat
"""

import argparse
import ipaddress
from typing import Optional


class ConfigManager:
    """
    Русский:
        Менеджер конфигурации приложения IPv4-чат
        Аргументы:
            ip: IPv4 адрес для приема сообщений
            port: порт для приема сообщений
            enable_logging: включить запись логов в файл
        Возвращаемое значение: None
    
    English:
        Configuration manager for IPv4 Chat application
        Arguments:
            ip: IPv4 address for receiving messages
            port: port for receiving messages
            enable_logging: enable log file writing
        Returns: None
    """
    
    def __init__(self, ip: str, port: int, enable_logging: bool = False):
        self.ip = ip
        self.port = port
        self.enable_logging = enable_logging
    
    @classmethod
    def from_command_line(cls) -> 'ConfigManager':
        """
        Русский:
            Создание конфигурации из аргументов командной строки
            Аргументы: None
            Возвращаемое значение: объект ConfigManager
    
        English:
            Create configuration from command line arguments
            Arguments: None
            Returns: ConfigManager object
        """
        parser = argparse.ArgumentParser(
            description='IPv4 Chat - UDP broadcast chat application',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Примеры использования / Usage examples:
  python main.py --ip 192.168.1.100 --port 1234
  python main.py --ip 192.168.1.100 --port 1234 --log
            """
        )
        
        parser.add_argument(
            '--ip',
            required=True,
            help='IPv4 адрес для приема сообщений / IPv4 address for receiving messages'
        )
        
        parser.add_argument(
            '--port',
            type=int,
            required=True,
            help='Порт для приема сообщений / Port for receiving messages'
        )
        
        parser.add_argument(
            '--log',
            action='store_true',
            help='Включить запись логов в файл / Enable log file writing'
        )
        
        args = parser.parse_args()
        
        # Валидация IPv4 адреса
        try:
            ipaddress.IPv4Address(args.ip)
        except ipaddress.AddressValueError:
            parser.error(f"Неверный IPv4 адрес: {args.ip}")
        
        # Валидация порта
        if not (1 <= args.port <= 65535):
            parser.error(f"Порт должен быть в диапазоне 1-65535: {args.port}")
        
        return cls(args.ip, args.port, args.log)
    
    def __str__(self) -> str:
        return f"Config(ip={self.ip}, port={self.port}, logging={'enabled' if self.enable_logging else 'disabled'})"


if __name__ == "__main__":
    # Тестирование конфигурации
    try:
        config = ConfigManager.from_command_line()
        print(f"Конфигурация загружена: {config}")
    except SystemExit:
        print("Ошибка в аргументах командной строки")
