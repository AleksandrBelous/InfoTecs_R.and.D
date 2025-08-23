"""
Система логирования для IPv4-чата
Logging system for IPv4 Chat
"""

import os
import threading
from contextlib import contextmanager
from datetime import datetime


class LoggerManager:
    """
    Русский:
        Менеджер логирования с поддержкой стека вызовов и отступов
        Аргументы:
            log_dir: папка для лог-файлов
            enable_file_logging: включить запись в файл
        Возвращаемое значение: None
    
    English:
        Logging manager with call stack and indentation support
        Arguments:
            log_dir: directory for log files
            enable_file_logging: enable file logging
        Returns: None
    """

    def __init__(self, log_dir: str = "logs", enable_file_logging: bool = False):
        self.log_dir = log_dir
        self.enable_file_logging = enable_file_logging
        self.call_stack = []
        self.lock = threading.RLock()
        self.log_file = None
        self.log_file_path = None
        self.console_output = True

        if enable_file_logging:
            self._setup_file_logging()

    def _setup_file_logging(self) -> None:
        """
        Русский:
            Настройка файлового логирования
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Setup file logging
            Arguments: None
            Returns: None
        """
        try:
            # Создаем папку для логов, если её нет
            if not os.path.exists(self.log_dir):
                try:
                    os.makedirs(self.log_dir, mode=0o755, exist_ok=True)
                    print(f"Создана директория для логов: {self.log_dir}")
                except PermissionError:
                    print(f"Ошибка прав доступа при создании директории {self.log_dir}")
                    # Пытаемся создать в домашней директории пользователя
                    home_dir = os.path.expanduser("~")
                    fallback_log_dir = os.path.join(home_dir, "chat_logs")
                    try:
                        os.makedirs(fallback_log_dir, mode=0o755, exist_ok=True)
                        self.log_dir = fallback_log_dir
                        print(f"Логи будут сохраняться в: {fallback_log_dir}")
                    except Exception as fallback_e:
                        print(f"Не удалось создать fallback директорию: {fallback_e}")
                        self.enable_file_logging = False
                        return
                except Exception as e:
                    print(f"Ошибка создания директории {self.log_dir}: {e}")
                    self.enable_file_logging = False
                    return

            # Проверяем права на запись в директорию
            if not os.access(self.log_dir, os.W_OK):
                print(f"Нет прав на запись в директорию {self.log_dir}")
                # Пытаемся создать в домашней директории
                home_dir = os.path.expanduser("~")
                fallback_log_dir = os.path.join(home_dir, "chat_logs")
                try:
                    os.makedirs(fallback_log_dir, mode=0o755, exist_ok=True)
                    self.log_dir = fallback_log_dir
                    print(f"Логи будут сохраняться в: {fallback_log_dir}")
                except Exception as fallback_e:
                    print(f"Не удалось создать fallback директорию: {fallback_e}")
                    self.enable_file_logging = False
                    return

            # Генерируем имя файла с датой и временем
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{timestamp}_chat.log"
            self.log_file_path = os.path.join(self.log_dir, filename)

            # Открываем файл для записи
            try:
                self.log_file = open(self.log_file_path, 'w', encoding='utf-8')
                print(f"Лог-файл создан: {self.log_file_path}")
            except PermissionError:
                print(f"Ошибка прав доступа при создании файла {self.log_file_path}")
                # Пытаемся создать в текущей директории
                try:
                    fallback_filename = f"{timestamp}_chat_fallback.log"
                    self.log_file_path = fallback_filename
                    self.log_file = open(fallback_filename, 'w', encoding='utf-8')
                    print(f"Лог-файл создан в текущей директории: {fallback_filename}")
                except Exception as fallback_e:
                    print(f"Не удалось создать fallback файл: {fallback_e}")
                    self.enable_file_logging = False
                    return
            except Exception as e:
                print(f"Ошибка создания лог-файла: {e}")
                self.enable_file_logging = False
                return

        except Exception as e:
            # Если не удалось создать файл, отключаем файловое логирование
            print(f"Критическая ошибка создания лог-файла: {e}")
            print("Файловое логирование отключено, логи будут выводиться только в консоль")
            self.enable_file_logging = False
            self.log_file = None

    def _write_log(self, level: str, message: str) -> None:
        """
        Русский:
            Запись лога в файл и консоль
            Аргументы:
                level: уровень логирования (INFO, ERROR, WARNING, DEBUG)
                message: сообщение для записи
            Возвращаемое значение: None
    
        English:
            Write log to file and console
            Arguments:
                level: log level (INFO, ERROR, WARNING, DEBUG)
                message: message to log
            Returns: None
        """
        with self.lock:
            # Формируем отступы для стека вызовов
            indent = "    " * len(self.call_stack)
            log_line = f"[{level}] {indent}{message}"

            # Выводим в консоль (если разрешено)
            if self.console_output:
                print(log_line)

            # Записываем в файл, если включено
            if self.enable_file_logging and self.log_file:
                try:
                    self.log_file.write(log_line + "\n")
                    self.log_file.flush()
                except Exception:
                    # Игнорируем ошибки записи в файл
                    pass

    def start_function(self, function_name: str) -> None:
        """
        Русский:
            Начать логирование функции (добавить в стек вызовов)
            Аргументы:
                function_name: имя функции
            Возвращаемое значение: None
    
        English:
            Start function logging (add to call stack)
            Arguments:
                function_name: function name
            Returns: None
        """
        with self.lock:
            self.call_stack.append(function_name)
            self._write_log("INF", f"[+] Start {function_name}")

    def stop_function(self, function_name: str) -> None:
        """
        Русский:
            Закончить логирование функции (убрать из стека вызовов)
            Аргументы:
                function_name: имя функции
            Возвращаемое значение: None
    
        English:
            Stop function logging (remove from call stack)
            Arguments:
                function_name: function name
            Returns: None
        """
        with self.lock:
            if self.call_stack and self.call_stack[-1] == function_name:
                self._write_log("INF", f"[-] Stop {function_name}")
                self.call_stack.pop()
            else:
                # Если стек не соответствует, логируем ошибку
                self._write_log("WAR", f"Call stack mismatch for {function_name}")

    @contextmanager
    def context(self, function_name: str):
        """
        Русский:
            Контекстный менеджер для автоматического логирования входа/выхода из функции
            Аргументы:
                function_name: имя функции
            Возвращаемое значение: контекстный менеджер
    
        English:
            Context manager for automatic function entry/exit logging
            Arguments:
                function_name: function name
            Returns: context manager
        """
        self.start_function(function_name)
        try:
            yield
        finally:
            self.stop_function(function_name)

    def info(self, message: str) -> None:
        """
        Русский:
            Логировать информационное сообщение
            Аргументы:
                message: сообщение для логирования
            Возвращаемое значение: None
    
        English:
            Log informational message
            Arguments:
                message: message to log
            Returns: None
        """
        self._write_log("INF", message)

    def warning(self, message: str) -> None:
        """
        Русский:
            Логировать предупреждение
            Аргументы:
                message: сообщение для логирования
            Возвращаемое значение: None
    
        English:
            Log warning message
            Arguments:
                message: message to log
            Returns: None
        """
        self._write_log("WAR", message)

    def error(self, message: str) -> None:
        """
        Русский:
            Логировать ошибку
            Аргументы:
                message: сообщение для логирования
            Возвращаемое значение: None
    
        English:
            Log error message
            Arguments:
                message: message to log
            Returns: None
        """
        self._write_log("ERR", message)

    def debug(self, message: str) -> None:
        """
        Русский:
            Логировать отладочное сообщение
            Аргументы:
                message: сообщение для логирования
            Возвращаемое значение: None
    
        English:
            Log debug message
            Arguments:
                message: message to log
            Returns: None
        """
        self._write_log("DBG", message)

    def get_call_stack(self) -> list[str]:
        """
        Русский:
            Получить текущий стек вызовов
            Аргументы: None
            Возвращаемое значение: список имен функций в стеке
    
        English:
            Get current call stack
            Arguments: None
            Returns: list of function names in stack
        """
        with self.lock:
            return self.call_stack.copy()

    def cleanup(self) -> None:
        """
        Русский:
            Очистка ресурсов логирования
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Cleanup logging resources
            Arguments: None
            Returns: None
        """
        if self.log_file:
            try:
                self.log_file.close()
            except Exception:
                pass
            self.log_file = None

    def set_console_output(self, enabled: bool) -> None:
        """
        Русский:
            Включить или отключить вывод логов в консоль (STDOUT)
            Аргументы:
                enabled: True для включения, False для отключения
            Возвращаемое значение: None
        
        English:
            Enable or disable console (STDOUT) log output
            Arguments:
                enabled: True to enable, False to disable
            Returns: None
        """
        with self.lock:
            self.console_output = bool(enabled)


if __name__ == "__main__":
    # Тестирование LoggerManager
    logger = LoggerManager(enable_file_logging=True)

    with logger.context("main"):
        logger.info("Тестирование системы логирования")

        with logger.context("test_function"):
            logger.info("Внутри тестовой функции")
            logger.warning("Предупреждение")
            logger.error("Ошибка")
            logger.debug("Отладочная информация")

        logger.info("Тестирование завершено")

    logger.cleanup()
