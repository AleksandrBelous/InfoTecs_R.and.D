# Makefile для UDP чата
# Makefile for UDP chat

# Переменные по умолчанию
# Default variables
IP ?= 127.0.0.1
PORT ?= 8888

# Цель по умолчанию
# Default target
.PHONY: run
run:
	@echo "Запуск чата на $(IP):$(PORT)"
	@echo "Running chat on $(IP):$(PORT)"
	python3 main.py --ip $(IP) --port $(PORT)

# Цель для тестирования
# Test target
.PHONY: test
test:
	@echo "Тестирование модулей..."
	@echo "Testing modules..."
	python3 -c "import args; import net; import ui; print('Все модули импортируются корректно')"

# Цель для очистки
# Clean target
.PHONY: clean
clean:
	@echo "Очистка временных файлов..."
	@echo "Cleaning temporary files..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Цель для помощи
# Help target
.PHONY: help
help:
	@echo "Доступные цели:"
	@echo "Available targets:"
	@echo "  run     - Запустить чат (IP=127.0.0.1, PORT=8888)"
	@echo "  test    - Протестировать импорт модулей"
	@echo "  clean   - Очистить временные файлы"
	@echo "  help    - Показать эту справку"
	@echo ""
	@echo "Примеры использования:"
	@echo "Usage examples:"
	@echo "  make run IP=192.168.1.100 PORT=9999"
	@echo "  make run IP=10.0.0.5 PORT=7777"
