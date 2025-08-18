"""
Система логирования для IPv4-чата
Logging system for IPv4 Chat
"""

import os
import threading
import time
from datetime import datetime
from typing import Optional
from contextlib import contextmanager


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
        self.lock = threading.Lock()
        self.log_file = None
        self.log_file_path = None
        
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
                os.makedirs(self.log_dir)
            
            # Генерируем имя файла с датой и временем
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{timestamp}_chat.log"
            self.log_file_path = os.path.join(self.log_dir, filename)
            
            # Открываем файл для записи
            self.log_file = open(self.log_file_path, 'w', encoding='utf-8')
            
        except Exception as e:
            # Если не удалось создать файл, отключаем файловое логирование
            print(f"Ошибка создания лог-файла: {e}")
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
            
            # Выводим в консоль
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
            self._write_log("INFO", f"Start {function_name}")
    
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
                self._write_log("INFO", f"Stop {function_name}")
                self.call_stack.pop()
            else:
                # Если стек не соответствует, логируем ошибку
                self._write_log("WARNING", f"Call stack mismatch for {function_name}")
    
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
        self._write_log("INFO", message)
    
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
        self._write_log("WARNING", message)
    
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
        self._write_log("ERROR", message)
    
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
        self._write_log("DEBUG", message)
    
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
