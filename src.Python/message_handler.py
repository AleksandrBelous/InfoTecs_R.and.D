"""
Обработчик сообщений для IPv4-чата
Message handler for IPv4 Chat
"""

import json
from typing import Optional, Dict


class MessageHandler:
    """
    Русский:
        Обработчик сообщений с JSON форматом и валидацией
        Аргументы:
            logger: менеджер логирования
        Возвращаемое значение: None
    
    English:
        Message handler with JSON format and validation
        Arguments:
            logger: logging manager
        Returns: None
    """

    def __init__(self, logger):
        self.logger = logger
        self.max_message_size = 1000  # Максимальный размер сообщения в байтах (ТЗ требование)

    def _create_message_dict(self, nickname: str, message: str) -> Dict[str, str]:
        """
        Русский:
            Создать словарь сообщения
            Аргументы:
                nickname: никнейм отправителя
                message: текст сообщения
            Возвращаемое значение: словарь сообщения
    
        English:
            Create message dictionary
            Arguments:
                nickname: sender nickname
                message: message text
            Returns: message dictionary
        """
        return {
                'nick': nickname.strip(),
                'msg' : message.strip()
                }

    def validate_message_length(self, nickname: str, message: str) -> bool:
        """
        Русский:
            Проверить, что сообщение не превышает лимит в 1000 байт (требование ТЗ)
            Аргументы:
                nickname: никнейм отправителя
                message: текст сообщения
            Возвращаемое значение: True если сообщение валидно, False иначе
    
        English:
            Check that message doesn't exceed 1000 bytes limit (ТЗ requirement)
            Arguments:
                nickname: sender nickname
                message: message text
            Returns: True if message is valid, False otherwise
        """
        try:
            # Создаем тестовое сообщение для проверки размера
            test_message = self._create_message_dict(nickname, message)
            serialized = json.dumps(test_message, ensure_ascii=False)
            message_bytes = serialized.encode('utf-8')

            if len(message_bytes) <= self.max_message_size:
                self.logger.debug(f"Сообщение валидно: {len(message_bytes)} байт")
                return True
            else:
                self.logger.warning(
                        f"Сообщение превышает лимит: {len(message_bytes)} > {self.max_message_size} байт"
                        )
                return False

        except Exception as e:
            self.logger.error(f"Ошибка валидации сообщения: {e}")
            return False

    def build_outgoing_message(self, nickname: str, message: str) -> Optional[bytes]:
        """
        Русский:
            Создать исходящее сообщение в JSON формате
            Аргументы:
                nickname: никнейм отправителя
                message: текст сообщения
            Возвращаемое значение: байты сообщения или None при ошибке
    
        English:
            Create outgoing message in JSON format
            Arguments:
                nickname: sender nickname
                message: message text
            Returns: message bytes or None on error
        """
        try:
            if not self.validate_message_length(nickname, message):
                return None

            message_dict = self._create_message_dict(nickname, message)
            serialized = json.dumps(message_dict, ensure_ascii=False)
            message_bytes = serialized.encode('utf-8')

            self.logger.debug(f"Создано исходящее сообщение: {len(message_bytes)} байт")
            return message_bytes

        except Exception as e:
            self.logger.error(f"Ошибка создания исходящего сообщения: {e}")
            return None

    def parse_incoming_message(self, raw_data: bytes) -> Optional[Dict[str, str]]:
        """
        Русский:
            Парсить входящее сообщение из JSON формата
            Аргументы:
                raw_data: сырые байты сообщения
            Возвращаемое значение: словарь с полями nick и msg или None при ошибке
    
        English:
            Parse incoming message from JSON format
            Arguments:
                raw_data: raw message bytes
            Returns: dictionary with nick and msg fields or None on error
        """
        try:
            # Декодируем байты в строку
            message_str = raw_data.decode('utf-8')

            # Парсим JSON
            message_dict = json.loads(message_str)

            # Базовые проверки
            if not isinstance(message_dict, dict):
                return None

            if 'nick' not in message_dict or 'msg' not in message_dict:
                return None

            nickname = str(message_dict['nick']).strip()
            message = str(message_dict['msg']).strip()

            # Проверяем, что поля не пустые
            if not nickname or not message:
                return None

            self.logger.debug(f"Успешно распарсено сообщение от {nickname}")
            return {
                    'nick': nickname,
                    'msg' : message
                    }

        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        except Exception as e:
            self.logger.error(f"Ошибка при парсинге сообщения: {e}")
            return None


if __name__ == "__main__":
    # Тестирование MessageHandler
    from logger_manager import LoggerManager

    logger = LoggerManager()
    handler = MessageHandler(logger)

    # Тест валидации длины
    print("=== Тест валидации длины ===")
    long_message = "A" * 500  # Длинное сообщение
    result = handler.validate_message_length("test_user", long_message)
    print(f"Длинное сообщение валидно: {result}")

    # Тест создания исходящего сообщения
    print("\n=== Тест создания исходящего сообщения ===")
    outgoing = handler.build_outgoing_message("test_user", "Привет всем!")
    if outgoing:
        print(f"Создано сообщение: {outgoing}")
        print(f"Размер: {len(outgoing)} байт")

    # Тест парсинга входящего сообщения
    print("\n=== Тест парсинга входящего сообщения ===")
    if outgoing:
        parsed = handler.parse_incoming_message(outgoing)
        print(f"Распарсено: {parsed}")

    # Тест некорректного сообщения
    print("\n=== Тест некорректного сообщения ===")
    bad_message = b'{"invalid": "message"}'
    parsed = handler.parse_incoming_message(bad_message)
    print(f"Некорректное сообщение: {parsed}")

    logger.cleanup()
