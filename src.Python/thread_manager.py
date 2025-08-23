"""
Менеджер потоков для IPv4-чата
Thread Manager for IPv4 Chat
"""

import threading
import time
from typing import Optional
from queue import Queue


class ThreadManager:
    """
    Русский:
        Менеджер потоков для управления многопоточностью
        Аргументы:
            network: менеджер сетевых соединений
            ui: менеджер пользовательского интерфейса
            message_handler: обработчик сообщений
            logger: менеджер логирования
        Возвращаемое значение: None
    
    English:
        Thread manager for managing multithreading
        Arguments:
            network: network connection manager
            ui: user interface manager
            message_handler: message handler
            logger: logging manager
        Returns: None
    """

    def __init__(self, network, ui, message_handler, logger):
        self.network = network
        self.ui = ui
        self.message_handler = message_handler
        self.logger = logger

        # Потоки
        self.receive_thread = None
        self.ui_thread = None

        # Состояние
        self.is_running = False
        self.lock = threading.Lock()

        # Очереди для обмена данными между потоками
        self.incoming_queue = Queue()
        self.outgoing_queue = Queue()

        # События для синхронизации
        self.stop_event = threading.Event()

    def start(self) -> bool:
        """
        Русский:
            Запуск всех потоков
            Аргументы: None
            Возвращаемое значение: True при успехе, False при ошибке
    
        English:
            Start all threads
            Arguments: None
            Returns: True on success, False on error
        """
        try:
            with self.lock:
                if self.is_running:
                    self.logger.warning("Потоки уже запущены")
                    return True

                # Сбрасываем событие остановки
                self.stop_event.clear()

                # Запускаем поток приема сообщений
                self.receive_thread = threading.Thread(
                        target=self._receive_worker,
                        name="ReceiveThread",
                        daemon=True
                        )
                self.receive_thread.start()

                # Запускаем поток UI (в главном потоке)
                self.ui_thread = threading.Thread(
                        target=self._ui_worker,
                        name="UIThread",
                        daemon=True
                        )
                self.ui_thread.start()

                self.is_running = True
                self.logger.info("Все потоки запущены")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка запуска потоков: {e}")
            return False

    def stop(self) -> None:
        """
        Русский:
            Остановка всех потоков
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Stop all threads
            Arguments: None
            Returns: None
        """
        with self.lock:
            if not self.is_running:
                return

            # Устанавливаем событие остановки
            self.stop_event.set()

            # Ждем завершения потоков
            if self.receive_thread and self.receive_thread.is_alive():
                self.receive_thread.join(timeout=2.0)

            if self.ui_thread and self.ui_thread.is_alive():
                self.ui_thread.join(timeout=2.0)

            self.is_running = False
            self.logger.info("Все потоки остановлены")

    def join(self, timeout: Optional[float] = None) -> None:
        """
        Русский:
            Ожидание завершения всех потоков
            Аргументы:
                timeout: таймаут ожидания в секундах
            Возвращаемое значение: None
    
        English:
            Wait for all threads to complete
            Arguments:
                timeout: timeout in seconds
            Returns: None
        """
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=timeout)

        if self.ui_thread and self.ui_thread.is_alive():
            self.ui_thread.join(timeout=timeout)

    def _receive_worker(self) -> None:
        """
        Русский:
            Рабочий поток для приема сообщений
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Worker thread for receiving messages
            Arguments: None
            Returns: None
        """
        self.logger.info("Поток приема сообщений запущен")

        try:
            while not self.stop_event.is_set():
                # Принимаем сообщение
                result = self.network.receive_once()

                if result:
                    data, addr = result

                    # Парсим сообщение
                    parsed_message = self.message_handler.parse_incoming_message(data)

                    if parsed_message:
                        # Добавляем в очередь для UI (все сообщения без фильтрации)
                        self.incoming_queue.put({
                                'nickname' : parsed_message['nick'],
                                'message'  : parsed_message['msg'],
                                'sender_ip': addr[0],  # ТЗ: IP отправителя из UDP заголовка
                                'address'  : addr  # Полная информация о UDP пакете
                                }
                                )

                        self.logger.debug(f"Сообщение от {addr[0]}:{addr[1]} добавлено в очередь")
                    else:
                        self.logger.warning(f"Не удалось распарсить сообщение от {addr[0]}:{addr[1]}")

                # Небольшая пауза для снижения нагрузки на CPU
                time.sleep(0.01)

        except Exception as e:
            self.logger.error(f"Ошибка в потоке приема: {e}")
        finally:
            self.logger.info("Поток приема сообщений завершен")

    def _ui_worker(self) -> None:
        """
        Русский:
            UI рабочий поток (обработка входящих сообщений)
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            UI worker thread (handling incoming messages)
            Arguments: None
            Returns: None
        """
        self.logger.info("UI поток запущен")

        try:
            while not self.stop_event.is_set():
                # Проверяем входящие сообщения
                try:
                    while not self.incoming_queue.empty():
                        message_data = self.incoming_queue.get_nowait()

                        # Отображаем сообщение в UI - ТЗ: выводить адрес отправителя, nickname и сообщение
                        sender_ip = message_data.get('sender_ip')  # IP отправителя из сообщения
                        self.ui.display_message(
                                message_data['nickname'],
                                message_data['message'],
                                sender_ip=sender_ip
                                )

                        self.logger.debug(f"Сообщение отображается в UI: {message_data['nickname']}")

                except:
                    # Очередь пуста или ошибка
                    pass

                # Небольшая пауза
                time.sleep(0.1)

        except Exception as e:
            self.logger.error(f"Ошибка в UI потоке: {e}")
        finally:
            self.logger.info("UI поток завершен")

    def send_message(self, message: str) -> bool:
        """
        Русский:
            Отправка сообщения через сетевой менеджер
            Аргументы:
                message: текст сообщения
            Возвращаемое значение: True при успехе, False при ошибке
    
        English:
            Send message through network manager
            Arguments:
                message: message text
            Returns: True on success, False on error
        """
        try:
            # Получаем никнейм из UI
            nickname = self.ui.get_nickname()

            # Создаем исходящее сообщение
            outgoing_data = self.message_handler.build_outgoing_message(nickname, message)

            if not outgoing_data:
                self.logger.warning("Не удалось создать исходящее сообщение")
                return False

            # ТЗ: отправляем UDP-датаграмму на broadcast 255.255.255.255 и указанный порт
            if self.network.send_broadcast(outgoing_data):
                self.logger.info(f"Сообщение отправлено: {message}")
                return True
            else:
                self.logger.error("Ошибка отправки сообщения")
                return False

        except Exception as e:
            self.logger.error(f"Ошибка отправки сообщения: {e}")
            return False

    def get_status(self) -> dict:
        """
        Русский:
            Получить статус потоков
            Аргументы: None
            Возвращаемое значение: словарь со статусом
    
        English:
            Get thread status
            Arguments: None
            Returns: dictionary with status
        """
        with self.lock:
            return {
                    'is_running'          : self.is_running,
                    'receive_thread_alive': self.receive_thread.is_alive() if self.receive_thread else False,
                    'ui_thread_alive'     : self.ui_thread.is_alive() if self.ui_thread else False,
                    'incoming_queue_size' : self.incoming_queue.qsize(),
                    'outgoing_queue_size' : self.outgoing_queue.qsize(),
                    'stop_event_set'      : self.stop_event.is_set()
                    }

    def is_ready(self) -> bool:
        """
        Русский:
            Проверить готовность к работе
            Аргументы: None
            Возвращаемое значение: True если готов, False иначе
    
        English:
            Check if ready for operation
            Arguments: None
            Returns: True if ready, False otherwise
        """
        with self.lock:
            return (self.is_running and
                    self.receive_thread and self.receive_thread.is_alive() and
                    self.ui_thread and self.ui_thread.is_alive())


if __name__ == "__main__":
    # Тестирование ThreadManager (без реальных компонентов)
    from logger_manager import LoggerManager

    logger = LoggerManager()


    # Создаем заглушки для тестирования
    class MockNetwork:
        def receive_once(self): return None

        def send_broadcast(self, data): return True

        def send_local(self, data): return True


    class MockUI:
        def get_nickname(self):
            return "test_user"

        def display_message(self, nick, msg, message_type="info", sender_ip=None):
            if sender_ip:
                print(f"{sender_ip} [{nick}]: {msg}")  # ТЗ: показываем IP отправителя
            else:
                print(f"[{nick}]: {msg}")


    class MockMessageHandler:
        def build_outgoing_message(self, nick, msg): return b'{"nick":"test","msg":"test"}'

        def parse_incoming_message(self, data): return { 'nick': 'test', 'msg': 'test' }


    network = MockNetwork()
    ui = MockUI()
    message_handler = MockMessageHandler()

    thread_manager = ThreadManager(network, ui, message_handler, logger)

    print("=== Тест ThreadManager ===")
    print(f"Статус: {thread_manager.get_status()}")

    logger.cleanup()
