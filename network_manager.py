"""
Сетевой менеджер для IPv4-чата
Network manager for IPv4 Chat
"""

import socket
import threading
from typing import Optional, Tuple, Any


class NetworkManager:
    """
    Русский:
        Менеджер сетевых соединений для UDP broadcast чата
        Аргументы:
            bind_ip: IPv4 адрес для приема сообщений
            port: порт для приема сообщений
            logger: менеджер логирования
        Возвращаемое значение: None
    
    English:
        Network connection manager for UDP broadcast chat
        Arguments:
            bind_ip: IPv4 address for receiving messages
            port: port for receiving messages
            logger: logging manager
        Returns: None
    """
    
    def __init__(self, bind_ip: str, port: int, logger):
        self.bind_ip = bind_ip
        self.port = port
        self.logger = logger
        
        # Сокеты
        self.receive_socket = None
        self.send_socket = None
        
        # Состояние
        self.is_open = False
        self.lock = threading.Lock()
        
        # Настройки
        self.receive_timeout = 1.0  # Таймаут приема в секундах
        self.buffer_size = 2048      # Размер буфера приема
    
    def open(self) -> bool:
        """
        Русский:
            Открыть сетевые соединения и настроить сокеты
            Аргументы: None
            Возвращаемое значение: True при успехе, False при ошибке
    
        English:
            Open network connections and configure sockets
            Arguments: None
            Returns: True on success, False on error
        """
        try:
            with self.lock:
                if self.is_open:
                    self.logger.warning("Сетевые соединения уже открыты")
                    return True
                
                # Создаем сокет для приема
                self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.receive_socket.settimeout(self.receive_timeout)
                
                # Привязываем сокет к адресу и порту
                self.receive_socket.bind((self.bind_ip, self.port))
                
                # Создаем сокет для отправки
                self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                
                self.is_open = True
                self.logger.info(f"Сетевые соединения открыты: {self.bind_ip}:{self.port}")
                return True
                
        except Exception as e:
            self.logger.error(f"Ошибка открытия сетевых соединений: {e}")
            self._cleanup_sockets()
            return False
    
    def close(self) -> None:
        """
        Русский:
            Закрыть сетевые соединения
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Close network connections
            Arguments: None
            Returns: None
        """
        with self.lock:
            if not self.is_open:
                return
            
            self._cleanup_sockets()
            self.is_open = False
            self.logger.info("Сетевые соединения закрыты")
    
    def _cleanup_sockets(self) -> None:
        """
        Русский:
            Очистка сокетов
            Аргументы: None
            Возвращаемое значение: None
    
        English:
            Cleanup sockets
            Arguments: None
            Returns: None
        """
        if self.receive_socket:
            try:
                self.receive_socket.close()
            except Exception:
                pass
            self.receive_socket = None
        
        if self.send_socket:
            try:
                self.send_socket.close()
            except Exception:
                pass
            self.send_socket = None
    
    def set_timeout(self, seconds: float) -> None:
        """
        Русский:
            Установить таймаут приема сообщений
            Аргументы:
                seconds: таймаут в секундах
            Возвращаемое значение: None
    
        English:
            Set receive timeout
            Arguments:
                seconds: timeout in seconds
            Returns: None
        """
        self.receive_timeout = seconds
        if self.receive_socket:
            try:
                self.receive_socket.settimeout(seconds)
                self.logger.debug(f"Таймаут приема установлен: {seconds} сек")
            except Exception as e:
                self.logger.warning(f"Не удалось установить таймаут: {e}")
    
    def receive_once(self, buffer_size: int = None) -> Optional[Tuple[bytes, Tuple[str, int]]]:
        """
        Русский:
            Принять одно UDP сообщение
            Аргументы:
                buffer_size: размер буфера приема (опционально)
            Возвращаемое значение: кортеж (данные, адрес) или None при ошибке
    
        English:
            Receive one UDP message
            Arguments:
                buffer_size: receive buffer size (optional)
            Returns: tuple (data, address) or None on error
        """
        if not self.is_open or not self.receive_socket:
            self.logger.warning("Попытка приема при закрытых соединениях")
            return None
        
        try:
            buffer = buffer_size or self.buffer_size
            data, addr = self.receive_socket.recvfrom(buffer)
            
            if data:
                self.logger.debug(f"Получено сообщение от {addr[0]}:{addr[1]}, размер: {len(data)} байт")
                return data, addr
            else:
                return None
                
        except socket.timeout:
            # Таймаут - это нормально, не логируем
            return None
        except Exception as e:
            self.logger.error(f"Ошибка приема сообщения: {e}")
            return None
    
    def send_broadcast(self, payload: bytes) -> bool:
        """
        Русский:
            Отправить broadcast сообщение
            Аргументы:
                payload: данные для отправки
            Возвращаемое значение: True при успехе, False при ошибке
    
        English:
            Send broadcast message
            Arguments:
                payload: data to send
            Returns: True on success, False on error
        """
        if not self.is_open or not self.send_socket:
            self.logger.warning("Попытка отправки при закрытых соединениях")
            return False
        
        try:
            # Отправляем на broadcast адрес
            broadcast_addr = ('255.255.255.255', self.port)
            bytes_sent = self.send_socket.sendto(payload, broadcast_addr)
            
            if bytes_sent == len(payload):
                self.logger.debug(f"Broadcast отправлен: {bytes_sent} байт")
                return True
            else:
                self.logger.warning(f"Неполная отправка: {bytes_sent}/{len(payload)} байт")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка отправки broadcast: {e}")
            return False
    
    def get_status(self) -> dict:
        """
        Русский:
            Получить статус сетевых соединений
            Аргументы: None
            Возвращаемое значение: словарь со статусом
    
        English:
            Get network connection status
            Arguments: None
            Returns: dictionary with status
        """
        with self.lock:
            return {
                'is_open': self.is_open,
                'bind_ip': self.bind_ip,
                'port': self.port,
                'receive_socket': self.receive_socket is not None,
                'send_socket': self.send_socket is not None,
                'timeout': self.receive_timeout,
                'buffer_size': self.buffer_size
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
            return self.is_open and self.receive_socket and self.send_socket


if __name__ == "__main__":
    # Тестирование NetworkManager
    from logger_manager import LoggerManager
    import time
    
    logger = LoggerManager()
    network = NetworkManager("127.0.0.1", 12345, logger)
    
    print("=== Тест открытия соединений ===")
    if network.open():
        print("Соединения открыты успешно")
        print(f"Статус: {network.get_status()}")
        
        print("\n=== Тест отправки broadcast ===")
        test_message = b'{"nick": "test", "msg": "Hello!"}'
        if network.send_broadcast(test_message):
            print("Broadcast отправлен успешно")
        
        print("\n=== Тест приема (с таймаутом) ===")
        network.set_timeout(2.0)
        result = network.receive_once()
        if result:
            print(f"Получено: {result}")
        else:
            print("Таймаут приема (ожидаемо)")
        
        print("\n=== Закрытие соединений ===")
        network.close()
        print("Соединения закрыты")
    
    logger.cleanup()
