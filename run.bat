@echo off
REM Скрипт для запуска приложения Медицинский центр на Windows

REM Проверка наличия виртуального окружения
if not exist "venv" (
    echo Виртуальное окружение не найдено. Создание...
    python -m venv venv
    echo Виртуальное окружение создано.
)

REM Активация виртуального окружения
call venv\Scripts\activate.bat

REM Установка зависимостей
echo Установка зависимостей...
pip install -r requirements.txt

REM Запуск приложения
echo Запуск приложения...
python main.py

REM Деактивация виртуального окружения при выходе
call deactivate 