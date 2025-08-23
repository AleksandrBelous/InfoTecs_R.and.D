#!/usr/bin/env python3
"""
IPv4 Chat - UDP Broadcast Chat Application
IPv4 Чат - Приложение для обмена сообщениями через UDP broadcast

Usage / Использование:
    python main.py --ip <IPv4_ADDRESS> --port <PORT> [--log]

Examples / Примеры:
    python main.py --ip 192.168.1.100 --port 12345
    python main.py --ip 192.168.1.100 --port 12345 --log
"""

import sys
import curses
from config import ConfigManager
from logger_manager import LoggerManager
from chat_application import ChatApplication


def main(stdscr):
    """
    Русский:
        Главная функция приложения с curses UI
        Аргументы:
            stdscr: главное окно curses
        Возвращаемое значение: код выхода
    
    English:
        Main application function with curses UI
        Arguments:
            stdscr: main curses window
        Returns: exit code
    """
    try:
        # Загружаем конфигурацию из командной строки
        config = ConfigManager.from_command_line()

        # Создаем менеджер логирования
        logger = LoggerManager(
                log_dir="logs",
                enable_file_logging=config.enable_logging
                )

        # Логируем запуск
        with logger.context("main"):
            logger.info("Запуск IPv4-чата")
            logger.info(f"Конфигурация: {config}")

            # Создаем и инициализируем приложение
            app = ChatApplication(config, logger)

            if not app.initialize():
                logger.error("Ошибка инициализации приложения")
                return 1

            # Запускаем приложение
            if not app.start(stdscr=stdscr):
                logger.error("Ошибка запуска приложения")
                return 1

            # Основной цикл
            app.run()

            logger.info("Приложение завершено")
            return 0

    except KeyboardInterrupt:
        print("\nПрерывание пользователем")
        return 130
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        return 1
    finally:
        # Очистка ресурсов
        if 'logger' in locals():
            logger.cleanup()


if __name__ == "__main__":
    # Быстрая проверка аргументов перед запуском curses
    if len(sys.argv) <= 1:
        print("Использование: python main.py --ip <IP> --port <PORT> [--log]")
        print("Пример: python main.py --ip 127.0.0.1 --port 12345 --log")
        sys.exit(2)

    # Валидация аргументов перед curses
    try:
        _ = ConfigManager.from_command_line()
    except SystemExit as e:
        sys.exit(e.code)

    # Запуск с curses UI
    try:
        exit_code = curses.wrapper(main)
        sys.exit(exit_code)
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
        sys.exit(1)
