"""
Главное приложение IPv4-чата
Main Chat Application for IPv4 Chat
"""

import time


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

                # Создаем компоненты
                self.network_manager = NetworkManager(
                        self.config.ip,
                        self.config.port,
                        self.logger
                        )

                self.message_handler = MessageHandler(self.logger)

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
            # Простой запрос никнейма через консоль или UI, если доступен
            while True:
                try:
                    if self.ui_manager and getattr(self.ui_manager, 'is_initialized', False):
                        # Используем UI для запроса никнейма
                        self.ui_manager.update_status("Введите ваш никнейм и нажмите Enter")
                        user_input = self.ui_manager.get_user_input()
                        nickname = (user_input or "").strip()
                    else:
                        nickname = input("Введите ваш никнейм: ").strip()
                    if nickname and len(nickname) <= 50:
                        self.nickname = nickname
                        if self.ui_manager:
                            self.ui_manager.set_nickname(nickname)
                        self.logger.info(f"Никнейм установлен: {nickname}")
                        break
                    else:
                        if self.ui_manager and getattr(self.ui_manager, 'is_initialized', False):
                            self.ui_manager.update_status("Никнейм пуст или слишком длинный (<=50). Повторите ввод.")
                        else:
                            print("Никнейм не может быть пустым и должен быть не длиннее 50 символов")
                except (EOFError, KeyboardInterrupt):
                    if self.ui_manager and getattr(self.ui_manager, 'is_initialized', False):
                        self.ui_manager.update_status("Используется никнейм по умолчанию: User")
                    else:
                        print("\nИспользуем никнейм по умолчанию: User")
                    self.nickname = "User"
                    if self.ui_manager:
                        self.ui_manager.set_nickname(self.nickname)
                    break

        return self.nickname

    def start(self, stdscr=None) -> bool:
        """
        Русский:
            Запуск приложения
            Аргументы:
                stdscr: главное окно curses (опционально)
            Возвращаемое значение: True при успехе, False при ошибке
    
        English:
            Start the application
            Arguments:
                stdscr: main curses window (optional)
            Returns: True on success, False on error
        """
        try:
            with self.logger.context("start"):
                self.logger.info("Запуск приложения IPv4-чат")

                # Создаем UI менеджер
                from ui_manager import UIManager
                self.ui_manager = UIManager("User", self.logger)
                if stdscr is not None:
                    # Инициализируем UI до запроса никнейма
                    if not self.ui_manager.initialize_ui(stdscr):
                        self.logger.error("Ошибка инициализации UI")
                        return False
                    # Отключаем вывод логов в STDOUT, чтобы не ломать curses
                    try:
                        self.logger.set_console_output(False)
                    except Exception:
                        pass
                    # Показать подсказку в UI
                    self.ui_manager.update_status(
                            "Добро пожаловать! Введите ваш никнейм и нажмите Enter. Для выхода используйте /quit"
                            )
                else:
                    self.logger.info("Запуск в простом режиме (без UI)")

                # Получаем никнейм
                nickname = self.get_nickname()

                # Создаем менеджер потоков
                from thread_manager import ThreadManager
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
            Основной цикл работы приложения (упрощенный)
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Main application loop (simplified)
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

                # Основной цикл UI (упрощенный)
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
                'nickname'  : self.nickname,
                'config'    : {
                        'ip'             : self.config.ip,
                        'port'           : self.config.port,
                        'logging_enabled': self.config.enable_logging
                        },
                'components': {
                        'network': self.network_manager.get_status() if self.network_manager else None,
                        'threads': self.thread_manager.get_status() if self.thread_manager else None,
                        'ui'     : self.ui_manager.is_initialized if self.ui_manager else False
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
