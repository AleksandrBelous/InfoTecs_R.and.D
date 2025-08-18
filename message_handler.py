"""
Обработчик сообщений для IPv4-чата
Message handler for IPv4 Chat
"""

import json
from typing import Optional, Dict, Any


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
        self.max_message_size = 1000  # Максимальный размер сообщения в байтах
    
    def validate_message_length(self, nickname: str, message: str) -> bool:
        """
        Русский:
            Проверить, что сообщение не превышает лимит в 1000 байт
            Аргументы:
                nickname: никнейм отправителя
                message: текст сообщения
            Возвращаемое значение: True если сообщение валидно, False иначе
    
        English:
            Check that message doesn't exceed 1000 bytes limit
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
            
            # Проверяем обязательные поля
            if not isinstance(message_dict, dict):
                self.logger.warning("Входящее сообщение не является словарем")
                return None
            
            if 'nick' not in message_dict or 'msg' not in message_dict:
                self.logger.warning("Входящее сообщение не содержит обязательные поля nick и msg")
                return None
            
            nickname = message_dict['nick']
            message = message_dict['msg']
            
            # Проверяем типы полей
            if not isinstance(nickname, str) or not isinstance(message, str):
                self.logger.warning("Поля nick и msg должны быть строками")
                return None
            
            # Проверяем, что поля не пустые
            if not nickname.strip() or not message.strip():
                self.logger.warning("Поля nick и msg не могут быть пустыми")
                return None
            
            self.logger.debug(f"Успешно распарсено сообщение от {nickname}")
            return {
                'nick': nickname.strip(),
                'msg': message.strip()
            }
            
        except UnicodeDecodeError as e:
            self.logger.warning(f"Ошибка декодирования UTF-8: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.warning(f"Ошибка парсинга JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при парсинге сообщения: {e}")
            return None
    
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
            'msg': message.strip()
        }
    
    def get_message_info(self, message_bytes: bytes) -> Dict[str, Any]:
        """
        Русский:
            Получить информацию о сообщении без парсинга
            Аргументы:
                message_bytes: байты сообщения
            Возвращаемое значение: словарь с информацией о сообщении
    
        English:
            Get message information without parsing
            Arguments:
                message_bytes: message bytes
            Returns: dictionary with message information
        """
        try:
            message_str = message_bytes.decode('utf-8')
            message_dict = json.loads(message_str)
            
            return {
                'size_bytes': len(message_bytes),
                'size_chars': len(message_str),
                'has_nick': 'nick' in message_dict,
                'has_msg': 'msg' in message_dict,
                'is_valid_json': True
            }
        except Exception:
            return {
                'size_bytes': len(message_bytes),
                'size_chars': 'unknown',
                'has_nick': False,
                'has_msg': False,
                'is_valid_json': False
            }


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
