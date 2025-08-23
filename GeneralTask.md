# Минимальное ТЗ (мультифайл): «IPv4‑чат по широковещанию»

Цель — зафиксировать **простую архитектуру из нескольких файлов** для прототипа UDP‑чата по IPv4‑широковещанию, строго в
рамках исходного ТЗ и без лишних проверок/валидаций. Минимум ООП и разделение обязанностей: разбор аргументов отдельно,
сеть отдельно, UI отдельно.

---

## 1) Соответствие исходному ТЗ

* ОС: GNU/Linux. Язык: Python. Сборка: допускается `Makefile` с одной целью `run`.
* Обязательные параметры запуска: `--ip <IPv4>` и `--port <UDP>`.
* Два потока: приём (слушает порт) и ввод/отправка (шлёт на `255.255.255.255:<port>`).
* Сообщение ≤ **1000 байт UTF‑8**. Ввод ника — **после старта** (в UI).
* Вывод: `[src_ip] nick: text`.
* Никаких дополнительных проверок среды, персистентности ника, JSON/UUID и т.п. — **минимализм**.

---

## 2) Файловая структура (минимум)

```
project/
  main.py         # Точка входа: склейка модулей и запуск
  args.py         # Разбор CLI-аргументов (--ip, --port)
  net.py          # UdpReceiverThread, UdpSender (минимальные классы)
  ui.py    # CursesChatUI: 3 панели, ввод ника/сообщений
  Makefile        # (опц.) цель run
```

---

## 3) Ответственности модулей

### 3.1 main.py

* Импортирует `parse_args()` из `args.py`.
* Создаёт `UdpReceiverThread(queue, ip, port)` и `UdpSender(port)` из `net.py`.
* Передаёт оба объекта + очередь в `CursesChatUI` и вызывает `ui.run()`.
* По `KeyboardInterrupt` — мягко останавливает поток приёма (через атрибут `running=False`), закрывает сокеты и выходит.

### 3.2 args.py

* Функция `parse_args()` — возвращает `Namespace(ip: str, port: int)`.
* Если обязательных аргументов нет — печатает `--help` и выходит (стандартный `argparse`).

### 3.3 net.py

* **UdpSender**:

    * конструктор принимает `port: int`, создаёт UDP‑сокет, выставляет `SO_BROADCAST`.
    * метод `send(text: str)`: кодирует `text.encode('utf-8')`, проверяет `<=1000` байт; если ок —
      `sendto(data, ('255.255.255.255', self.port))`.
* **UdpReceiverThread** (наследник `threading.Thread`, `daemon=True`):

    * конструктор принимает `queue: Queue, ip: str, port: int`; создаёт UDP‑сокет, `SO_REUSEADDR`, `bind((ip, port))`,
      `settimeout(0.2)`.
    * атрибут `running: bool = True`.
    * `run()`: в цикле читает `recvfrom()`, складывает строки вида `f"[{src_ip}] {payload.decode('utf-8','replace')}"` в
      `queue`.
    * метод `stop()`: ставит `running=False` и закрывает сокет.

### 3.4 ui.py

* **CursesChatUI**:

    * `__init__(self, stdscr, sender: UdpSender, rx_queue: Queue, iface_ip: str, port: int)`
    * `run()` — главный цикл: рисует 3 панели, читает клавиши, по Enter отправляет; регулярно читает очередь и пополняет
      ленту.
    * Простая модель: без resize‑логики и сложного скролла. Хранить последние N (например, 500) строк.
    * До ввода ника приглашение: `nick: `; после — `>> `.
    * Отправляем **только** строки формата `"<nick>: <text>"`.

---

## 4) Потоки и взаимодействие

* `UdpReceiverThread` кладёт входящие строки в `Queue[str]`.
* `CursesChatUI.run()` в каждом тикe:

    * вычитывает все доступные строки из очереди и добавляет в `messages`;
    * перерисовывает панель сообщений;
    * обрабатывает ввод: ник → режим ввода; сообщение → `sender.send(f"{nick}: {text}")`.
* Локально отправленные сообщения **не** дублируем сразу — ждём сетевое эхо (минимум кода).

---

## 5) Поведение UI (минимум)

* Верх: одна строка `iface=<ip:port> | nick=<ник/—> | status=<OK/ошибка>` + разделительная линия.
* Центр: просто печать последних N строк; автопрокрутка вниз.
* Низ: приглашение (`nick:`/`>>`) и поле ввода; поддержка `Backspace` и `Enter` (достаточно `KEY_ENTER` и код 10).
* По `Ctrl+C` — выход (`KeyboardInterrupt`), очистка curses происходит через `curses.wrapper` в `main.py`.

---

## 6) Минимальные интерфейсы (сигнатуры)

```python
# args.py
from argparse import Namespace


def parse_args() -> Namespace:
    ...  # возвращает Namespace(ip=str, port=int)


# net.py
import threading
from queue import Queue


class UdpSender:
    def __init__(self, port: int): ...

    def send(self, text: str) -> None: ...  # проверка 1000 байт и sendto


class UdpReceiverThread(threading.Thread):
    def __init__(self, q: Queue, ip: str, port: int): ...

    def run(self): ...  # recvfrom -> q.put(f"[{src}] {text}")

    def stop(self): ...  # running=False; socket.close()


# ui.py
from queue import Queue


class CursesChatUI:
    def __init__(self, stdscr, sender: UdpSender, rx_q: Queue, iface_ip: str, port: int): ...

    def run(self) -> None: ...
```

---

## 7) Псевдокод минимальной логики

```python
# main.py
from curses import wrapper
from queue import Queue
from args import parse_args
from net import UdpSender, UdpReceiverThread
from ui import CursesChatUI


def ui_entry(stdscr, sender, rx_q, ip, port):
    ui = CursesChatUI(stdscr, sender, rx_q, ip, port)
    ui.run()


def main():
    a = parse_args()
    q = Queue()
    rx = UdpReceiverThread(q, a.ip, a.port)
    tx = UdpSender(a.port)
    rx.start()
    try:
        wrapper(ui_entry, tx, q, a.ip, a.port)
    finally:
        rx.stop()


if __name__ == "__main__":
    main()
```

---

## 8) Makefile (опц.)

```make
run:
	python3 main.py --ip $(IP) --port $(PORT)
```

---

## 9) Минимальные сценарии проверки

1. **Два процесса на одном хосте**: запустить два терминала с одинаковым `--port`; ввести ники; обменяться сообщениями.
2. **Две машины в одной сети**: запустить по экземпляру; порт один и тот же; убедиться, что сообщения приходят.
3. **Лимит 1000 байт**: строка ровно 1000 байт уходит; 1001 — не уходит, в статусе кратко «слишком длинно».

---

## 10) Что сознательно не делаем в этом прототипе

* Нет JSON/UUID, self‑echo фильтрации, логирования, resize‑обработки, сложного скролла.
* Нет расширенной валидации аргументов и окружения.
* Нет сохранения ника и конфиг‑файлов.

> Все эти вещи можно добавить позже поверх данной структуры, не ломая интерфейсы модулей.
