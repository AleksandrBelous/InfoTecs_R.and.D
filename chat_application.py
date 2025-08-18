"""
Главное приложение IPv4-чата
Main Chat Application for IPv4 Chat
"""

import signal
import sys
import time
from typing import Optional


class ChatApplication:
    """
    Русский:
        Главное приложение IPv4-чата, координирующее все компоненты
        Аргументы:
            config: конфигурация приложения
            logger: менеджер логирования
        Возвращаемое значение: None
    
    English:
        Main IPv4 Chat application, coordinating all components
        Arguments:
            config: application configuration
            logger: logging manager
        Returns: None
    """
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        
        # Компоненты приложения
        self.network_manager = None
        self.message_handler = None
        self.ui_manager = None
        self.thread_manager = None
        
        # Состояние
        self.is_running = False
        self.nickname = None
        
        # Обработчики сигналов
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self) -> None:
        """
        Русский:
            Настройка обработчиков сигналов для graceful shutdown
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Setup signal handlers for graceful shutdown
            Arguments: None
            Returns: None
        """
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame) -> None:
        """
        Русский:
            Обработчик сигналов для graceful shutdown
            Аргументы:
                signum: номер сигнала
                frame: текущий кадр стека
            Возвращаемое значение: None
    
        English:
            Signal handler for graceful shutdown
            Arguments:
                signum: signal number
                frame: current stack frame
            Returns: None
        """
        self.logger.info(f"Получен сигнал {signum}, завершаем работу...")
        self.stop()
        sys.exit(0)
    
    def initialize(self) -> bool:
        """
        Русский:
            Инициализация всех компонентов приложения
            Аргументы: None
            Возвращаемое значение: True при успехе, False при ошибке
    
        English:
            Initialize all application components
            Arguments: None
            Returns: True on success, False on error
        """
        try:
            with self.logger.context("initialize"):
                self.logger.info("Начало инициализации приложения")
                
                # Импортируем компоненты
                from network_manager import NetworkManager
                from message_handler import MessageHandler
                from ui_manager import UIManager
                from thread_manager import ThreadManager
                
                # Создаем компоненты
                self.network_manager = NetworkManager(
                    self.config.ip, 
                    self.config.port, 
                    self.logger
                )
                
                self.message_handler = MessageHandler(self.logger)
                
                # UI будет инициализирован позже в start()
                
                self.logger.info("Все компоненты созданы успешно")
                return True
                
        except Exception as e:
            self.logger.error(f"Ошибка инициализации: {e}")
            return False
    
    def get_nickname(self) -> str:
        """
        Русский:
            Получить никнейм пользователя (запросить если не задан)
            Аргументы: None
            Возвращаемое значение: никнейм пользователя
    
        English:
            Get user nickname (prompt if not set)
            Arguments: None
            Returns: user nickname
        """
        if not self.nickname:
            # Простой запрос никнейма через консоль
            while True:
                try:
                    nickname = input("Введите ваш никнейм: ").strip()
                    if nickname and len(nickname) <= 50:
                        self.nickname = nickname
                        self.logger.info(f"Никнейм установлен: {nickname}")
                        break
                    else:
                        print("Никнейм не может быть пустым и должен быть не длиннее 50 символов")
                except (EOFError, KeyboardInterrupt):
                    print("\nИспользуем никнейм по умолчанию: User")
                    self.nickname = "User"
                    break
        
        return self.nickname
    
    def start(self) -> bool:
        """
        Русский:
            Запуск приложения
            Аргументы: None
            Возвращаемое значение: True при успехе, False при ошибке
    
        English:
            Start the application
            Arguments: None
            Returns: True on success, False on error
        """
        try:
            with self.logger.context("start"):
                self.logger.info("Запуск приложения IPv4-чат")
                
                # Получаем никнейм
                nickname = self.get_nickname()
                
                # Создаем UI менеджер
                from ui_manager import UIManager
                self.ui_manager = UIManager(nickname, self.logger)
                
                # Создаем менеджер потоков
                self.thread_manager = ThreadManager(
                    self.network_manager,
                    self.ui_manager,
                    self.message_handler,
                    self.logger
                )
                
                # Открываем сетевые соединения
                if not self.network_manager.open():
                    self.logger.error("Не удалось открыть сетевые соединения")
                    return False
                
                # Запускаем потоки
                if not self.thread_manager.start():
                    self.logger.error("Не удалось запустить потоки")
                    return False
                
                self.is_running = True
                self.logger.info("Приложение успешно запущено")
                return True
                
        except Exception as e:
            self.logger.error(f"Ошибка запуска: {e}")
            return False
    
    def run(self) -> None:
        """
        Русский:
            Основной цикл работы приложения
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Main application loop
            Arguments: None
            Returns: None
        """
        if not self.is_running:
            self.logger.error("Приложение не запущено")
            return
        
        try:
            with self.logger.context("run"):
                self.logger.info("Вход в основной цикл приложения")
                
                # Обновляем статус
                self.ui_manager.update_status(
                    f"Подключен к {self.config.ip}:{self.config.port} | Слушаю сообщения..."
                )
                
                # Основной цикл UI
                while self.is_running:
                    try:
                        # Получаем ввод пользователя
                        user_input = self.ui_manager.get_user_input()
                        
                        if user_input is not None:
                            if user_input.lower() in ['/quit', '/exit', '/q']:
                                self.logger.info("Команда выхода получена")
                                break
                            elif user_input.strip():
                                # Отправляем сообщение
                                if self.thread_manager.send_message(user_input):
                                    self.logger.debug("Сообщение успешно отправлено")
                                else:
                                    self.logger.error("Ошибка отправки сообщения")
                        
                        # Небольшая пауза для снижения нагрузки
                        time.sleep(0.01)
                        
                    except KeyboardInterrupt:
                        self.logger.info("Прерывание пользователем")
                        break
                    except Exception as e:
                        self.logger.error(f"Ошибка в основном цикле: {e}")
                        break
                
                self.logger.info("Выход из основного цикла")
                
        except Exception as e:
            self.logger.error(f"Критическая ошибка в основном цикле: {e}")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """
        Русский:
            Остановка приложения
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Stop the application
            Arguments: None
            Returns: None
        """
        try:
            with self.logger.context("stop"):
                self.logger.info("Остановка приложения")
                
                self.is_running = False
                
                # Останавливаем потоки
                if self.thread_manager:
                    self.thread_manager.stop()
                    self.thread_manager.join()
                
                # Закрываем сетевые соединения
                if self.network_manager:
                    self.network_manager.close()
                
                # Очищаем UI
                if self.ui_manager:
                    self.ui_manager.cleanup()
                
                self.logger.info("Приложение остановлено")
                
        except Exception as e:
            self.logger.error(f"Ошибка при остановке: {e}")
    
    def get_status(self) -> dict:
        """
        Русский:
            Получить статус приложения
            Аргументы: None
            Возвращаемое значение: словарь со статусом
    
        English:
            Get application status
            Arguments: None
            Returns: dictionary with status
        """
        return {
            'is_running': self.is_running,
            'nickname': self.nickname,
            'config': {
                'ip': self.config.ip,
                'port': self.config.port,
                'logging_enabled': self.config.enable_logging
            },
            'components': {
                'network': self.network_manager.get_status() if self.network_manager else None,
                'threads': self.thread_manager.get_status() if self.thread_manager else None,
                'ui': self.ui_manager.is_initialized if self.ui_manager else False
            }
        }


if __name__ == "__main__":
    # Тестирование ChatApplication (без реальных компонентов)
    from logger_manager import LoggerManager
    from config import ConfigManager
    
    # Создаем тестовую конфигурацию
    config = ConfigManager("127.0.0.1", 12345, True)
    logger = LoggerManager(enable_file_logging=True)
    
    app = ChatApplication(config, logger)
    
    print("=== Тест ChatApplication ===")
    print(f"Конфигурация: {config}")
    
    if app.initialize():
        print("Инициализация успешна")
        print(f"Статус: {app.get_status()}")
    else:
        print("Ошибка инициализации")
    
    logger.cleanup()
