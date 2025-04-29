#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from database_connection import DatabaseConnection

DB_FILE = 'med_center.db'
BACKUP_FILE = DB_FILE + '.backup_' + __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')

# Переименовываем существующую БД в бэкап, если она есть
if os.path.exists(DB_FILE):
    os.rename(DB_FILE, BACKUP_FILE)
    print(f"Существующая база данных переименована в '{BACKUP_FILE}'")

# Инициализируем новую базу данных
db = DatabaseConnection()
# Здесь используем пароль по умолчанию для доступа к БД
if db.connect('1'):
    print("Новая база данных успешно создана и инициализирована")
else:
    print("Не удалось создать и инициализировать новую базу данных") 