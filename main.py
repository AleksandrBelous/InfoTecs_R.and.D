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


def main(stdscr=None):
    """
    Русский:
        Главная функция приложения
        Аргументы:
            stdscr: главное окно curses (для UI режима)
        Возвращаемое значение: None
    
    English:
        Main application function
        Arguments:
            stdscr: main curses window (for UI mode)
        Returns: None
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
            if not app.start():
                logger.error("Ошибка запуска приложения")
                return 1
            
            # Если запущен в UI режиме (с curses)
            if stdscr:
                # Инициализируем UI
                if not app.ui_manager.initialize_ui(stdscr):
                    logger.error("Ошибка инициализации UI")
                    return 1
                
                # Запускаем основной цикл
                app.run()
            else:
                # Простой режим без UI (для тестирования)
                logger.info("Запуск в простом режиме (без UI)")
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


def run_with_curses():
    """
    Русский:
        Запуск приложения с curses UI
        Аргументы: None
        Возвращаемое значение: код выхода
    
    English:
        Run application with curses UI
        Arguments: None
        Returns: exit code
    """
    try:
        return curses.wrapper(main)
    except Exception as e:
        print(f"Ошибка запуска curses: {e}")
        return 1


def run_simple():
    """
    Русский:
        Запуск приложения в простом режиме (без UI)
        Аргументы: None
        Возвращаемое значение: код выхода
    
    English:
        Run application in simple mode (without UI)
        Arguments: None
        Returns: exit code
    """
    try:
        return main()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        return 1


if __name__ == "__main__":
    # Проверяем, есть ли поддержка curses
    try:
        import curses
        exit_code = run_with_curses()
    except ImportError:
        print("Предупреждение: curses не поддерживается, запуск в простом режиме")
        exit_code = run_simple()
    
    sys.exit(exit_code)
