#!/bin/bash

# Определение директории скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Настройка виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения и установка зависимостей
source venv/bin/activate
pip install -r requirements.txt

# Запуск приложения
python3 main.py

# Деактивация виртуального окружения при выходе
deactivate 