"""
Менеджер пользовательского интерфейса для IPv4-чата
User Interface Manager for IPv4 Chat
"""

import curses
import threading
from datetime import datetime
from typing import Optional


class UIManager:
    """
    Русский:
        Менеджер пользовательского интерфейса с curses
        Аргументы:
            nickname: никнейм пользователя
            logger: менеджер логирования
        Возвращаемое значение: None
    
    English:
        User interface manager with curses
        Arguments:
            nickname: user nickname
            logger: logging manager
        Returns: None
    """

    def __init__(self, nickname: str, logger):
        self.nickname = nickname
        self.logger = logger

        # Окна curses
        self.stdscr = None
        self.status_win = None
        self.messages_win = None
        self.input_win = None

        # Размеры экрана
        self.max_y = 0
        self.max_x = 0

        # Состояние
        self.is_initialized = False
        self.lock = threading.Lock()

        # Простой список последних сообщений (без истории)
        self.recent_messages = []
        self.max_messages = 50  # Ограничение для производительности

    def initialize_ui(self, stdscr) -> bool:
        """
        Русский:
            Инициализация curses интерфейса
            Аргументы:
                stdscr: главное окно curses
            Возвращаемое значение: True при успехе, False при ошибке
    
        English:
            Initialize curses interface
            Arguments:
                stdscr: main curses window
            Returns: True on success, False on error
        """
        try:
            self.stdscr = stdscr

            # Настройки curses
            curses.curs_set(1)  # Показываем курсор
            curses.noecho()  # Не эхо ввода
            curses.cbreak()  # Режим cbreak

            # Получаем размеры экрана
            self.max_y, self.max_x = stdscr.getmaxyx()

            # Создаем окна
            self._create_windows()

            # Очищаем экран
            stdscr.clear()
            stdscr.refresh()

            self.is_initialized = True
            self.logger.info("UI интерфейс инициализирован")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка инициализации UI: {e}")
            return False

    def _create_windows(self) -> None:
        """
        Русский:
            Создание окон curses
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Create curses windows
            Arguments: None
            Returns: None
        """
        # Верхнее окно статуса (1 строка)
        self.status_win = curses.newwin(1, self.max_x, 0, 0)
        self.status_win.scrollok(False)

        # Среднее окно сообщений (оставшееся пространство минус 2 строки)
        messages_height = max(3, self.max_y - 3)
        self.messages_win = curses.newwin(messages_height, self.max_x, 1, 0)
        self.messages_win.scrollok(True)
        self.messages_win.idlok(True)

        # Нижнее окно ввода (2 строки)
        input_y = self.max_y - 2
        self.input_win = curses.newwin(2, self.max_x, input_y, 0)
        self.input_win.scrollok(False)

    def _refresh_messages(self) -> None:
        """
        Русский:
            Обновление области сообщений (упрощенное без истории)
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Refresh messages area (simplified without history)
            Arguments: None
            Returns: None
        """
        if not self.messages_win:
            return

        try:
            # Очищаем окно
            self.messages_win.clear()

            # Показываем последние сообщения, которые помещаются в окно
            max_rows = max(1, self.messages_win.getmaxyx()[0] - 1)
            to_show = self.recent_messages[-max_rows:]

            for i, msg in enumerate(to_show):
                try:
                    self.messages_win.addstr(i, 0, msg[:self.max_x - 1])
                except curses.error:
                    pass

            # Обновляем окно
            self.messages_win.refresh()

        except Exception as e:
            self.logger.error(f"Ошибка обновления сообщений: {e}")

    def display_message(self, nickname: str, message: str,
                        message_type: str = "info", sender_ip: str = None
                        ) -> None:
        """
        Русский:
            Отображение сообщения в области сообщений (ТЗ: с IPv4 адресом отправителя)
            Аргументы:
                nickname: никнейм отправителя
                message: текст сообщения
                message_type: тип сообщения
                sender_ip: IPv4 адрес отправителя (для ТЗ)
            Возвращаемое значение: None
    
        English:
            Display message in messages area (ТЗ: with sender IPv4 address)
            Arguments:
                nickname: sender nickname
                message: message text
                message_type: message type
                sender_ip: sender IPv4 address (for ТЗ)
            Returns: None
        """
        if not self.is_initialized:
            return

        try:
            with self.lock:
                # Формируем строку сообщения согласно ТЗ: "IPv4 адрес отправителя, его nickname, и полученное сообщение"
                timestamp = datetime.now().strftime("%H:%M:%S")
                if sender_ip:
                    # ТЗ: отображаем IP адрес отправителя
                    message_line = f"({timestamp}) {sender_ip} [{nickname}] {message}"
                else:
                    # Fallback для системных сообщений без IP
                    message_line = f"({timestamp}) [{nickname}] {message}"

                # Добавляем в простой список сообщений
                self.recent_messages.append(message_line)

                # Ограничиваем количество сообщений для производительности
                if len(self.recent_messages) > self.max_messages:
                    self.recent_messages = self.recent_messages[-self.max_messages:]

                # Сразу обновляем экран
                self._refresh_messages()

        except Exception as e:
            self.logger.error(f"Ошибка отображения сообщения: {e}")

    def update_status(self, status: str) -> None:
        """
        Русский:
            Обновление статусной строки
            Аргументы:
                status: текст статуса
            Возвращаемое значение: None
    
        English:
            Update status line
            Arguments:
                status: status text
            Returns: None
        """
        if not self.is_initialized or not self.status_win:
            return

        try:
            with self.lock:
                # Очищаем статусную строку
                self.status_win.clear()

                # Формируем статус
                status_text = f"[STATUS] {status}"
                if len(status_text) > self.max_x - 1:
                    status_text = status_text[:self.max_x - 4] + "..."

                # Отображаем статус
                self.status_win.addstr(0, 0, status_text)
                self.status_win.refresh()

        except Exception as e:
            self.logger.error(f"Ошибка обновления статуса: {e}")

    def get_user_input(self) -> Optional[str]:
        """
        Русский:
            Получение ввода от пользователя
            Аргументы: None
            Возвращаемое значение: введенная строка или None при ошибке
    
        English:
            Get user input
            Arguments: None
            Returns: input string or None on error
        """
        if not self.is_initialized or not self.input_win:
            return None

        try:
            # Рисуем приглашение под краткой блокировкой, затем освобождаем
            with self.lock:
                self.input_win.clear()
                prompt = ">> "
                self.input_win.addstr(0, 0, prompt)
                self.input_win.refresh()

            # Включаем эхо и читаем БЕЗ удержания lock, чтобы фоновые обновления могли идти
            curses.echo()
            max_len = max(1, self.max_x - len(prompt) - 1)
            user_input = self.input_win.getstr(0, len(prompt), max_len)
            curses.noecho()

            # Декодируем байты в строку
            if user_input:
                return user_input.decode('utf-8').strip()
            else:
                return ""

        except Exception as e:
            self.logger.error(f"Ошибка получения ввода: {e}")
            return None

    def cleanup(self) -> None:
        """
        Русский:
            Очистка curses интерфейса
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Cleanup curses interface
            Arguments: None
            Returns: None
        """
        if not self.is_initialized:
            return

        try:
            # Восстанавливаем настройки терминала
            curses.nocbreak()
            curses.echo()
            curses.endwin()

            self.is_initialized = False
            self.logger.info("UI интерфейс очищен")

        except Exception as e:
            self.logger.error(f"Ошибка очистки UI: {e}")

    def get_nickname(self) -> str:
        """
        Русский:
            Получить никнейм пользователя
            Аргументы: None
            Возвращаемое значение: никнейм пользователя
    
        English:
            Get user nickname
            Arguments: None
            Returns: user nickname
        """
        return self.nickname

    def set_nickname(self, nickname: str) -> None:
        """
        Русский:
            Установить новый никнейм пользователя
            Аргументы:
                nickname: новый никнейм
            Возвращаемое значение: None
    
        English:
            Set new user nickname
            Arguments:
                nickname: new nickname
            Returns: None
        """
        self.nickname = nickname.strip()
        self.logger.info(f"Никнейм изменен на: {self.nickname}")


if __name__ == "__main__":
    # Тестирование UIManager (только базовые функции без curses)
    from logger_manager import LoggerManager

    logger = LoggerManager()
    ui = UIManager("test_user", logger)

    print("=== Тест UIManager ===")
    print(f"Никнейм: {ui.get_nickname()}")

    ui.set_nickname("new_user")
    print(f"Новый никнейм: {ui.get_nickname()}")

    logger.cleanup()
