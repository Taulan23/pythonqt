#!/usr/bin/env python3

import sqlite3
import os

# Путь к файлу базы данных
db_path = 'med_center.db'

def fix_database():
    """Добавляет столбец gender в таблицу patients, если его нет"""
    print(f"Проверка базы данных: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Ошибка: файл базы данных {db_path} не найден")
        return False
    
    try:
        # Подключение к базе данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверка наличия столбца gender
        cursor.execute("PRAGMA table_info(patients)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'gender' not in column_names:
            print("Столбец 'gender' отсутствует в таблице 'patients', добавляем...")
            
            # Добавление столбца gender
            cursor.execute("ALTER TABLE patients ADD COLUMN gender VARCHAR(10) DEFAULT 'Мужской'")
            
            # Обновление существующих записей
            cursor.execute("UPDATE patients SET gender = 'Мужской' WHERE gender IS NULL")
            
            conn.commit()
            print("Столбец 'gender' успешно добавлен в таблицу 'patients'")
        else:
            print("Столбец 'gender' уже существует в таблице 'patients'")
        
        # Закрытие соединения
        conn.close()
        
        return True
    
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
        return False
    
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

if __name__ == "__main__":
    fix_database() 