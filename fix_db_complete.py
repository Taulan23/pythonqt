#!/usr/bin/env python3

import sqlite3
import os
import sys
from datetime import datetime

# Путь к файлу базы данных
DB_PATH = 'med_center.db'

def check_and_fix_db():
    """Проверяет и исправляет проблемы с базой данных"""
    print(f"--- Начало проверки и исправления базы данных: {DB_PATH} [{datetime.now()}] ---")
    
    if not os.path.exists(DB_PATH):
        print(f"Ошибка: файл базы данных {DB_PATH} не найден")
        return False
    
    print(f"База данных найдена: {DB_PATH}")
    
    conn = None
    try:
        # Подключение к базе данных
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Резервное копирование базы данных
        backup_path = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(DB_PATH, 'rb') as source:
            with open(backup_path, 'wb') as dest:
                dest.write(source.read())
        print(f"Создана резервная копия базы данных: {backup_path}")
        
        # 1. Проверка и добавление столбца gender в таблицу patients
        fix_gender_column(cursor, conn)
        
        # 2. Проверка таблицы пользователей
        check_users_table(cursor)
        
        # 3. Проверка таблицы appointments
        check_appointments_table(cursor)
        
        # 4. Проверка и исправление внешних ключей
        check_and_fix_foreign_keys(cursor, conn)

        # 5. Исправление проблем с обновлением записей
        fix_appointment_update_issues(cursor, conn)
        
        # 6. Исправление других потенциальных проблем
        fix_other_issues(cursor, conn)
        
        # 7. Проверка целостности базы данных
        check_db_integrity(cursor)
        
        # Закрытие соединения
        conn.close()
        print(f"--- Завершение проверки и исправления базы данных [{datetime.now()}] ---")
        return True
    
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {str(e)}")
        if conn:
            conn.close()
        return False
    
    except Exception as e:
        print(f"Непредвиденная ошибка: {str(e)}")
        if conn:
            conn.close()
        return False

def fix_gender_column(cursor, conn):
    """Проверяет и добавляет столбец gender в таблицу patients"""
    print("\n[Проверка столбца gender в таблице patients]")
    
    # Проверка наличия столбца gender
    cursor.execute("PRAGMA table_info(patients)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    if 'gender' not in column_names:
        try:
            print("Столбец 'gender' отсутствует в таблице 'patients', добавляем...")
            
            # Добавление столбца gender
            cursor.execute("ALTER TABLE patients ADD COLUMN gender VARCHAR(10) DEFAULT 'Мужской'")
            
            # Обновление существующих записей
            cursor.execute("UPDATE patients SET gender = 'Мужской' WHERE gender IS NULL")
            
            conn.commit()
            print("Столбец 'gender' успешно добавлен в таблицу 'patients'")
        
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении столбца 'gender': {str(e)}")
            return False
    else:
        print("Столбец 'gender' уже существует в таблице 'patients'")
    
    return True

def check_users_table(cursor):
    """Проверяет таблицу пользователей и выводит статистику"""
    print("\n[Проверка таблицы пользователей]")
    
    try:
        # Подсчет пользователей по ролям
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        role_counts = cursor.fetchall()
        
        print("Статистика пользователей по ролям:")
        for role, count in role_counts:
            print(f"  {role}: {count}")
        
        # Проверка пользователей с ролью doctor
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor'")
        doctor_count = cursor.fetchone()[0]
        
        # Проверка таблицы doctors
        cursor.execute("SELECT COUNT(*) FROM doctors")
        doctors_table_count = cursor.fetchone()[0]
        
        if doctor_count != doctors_table_count:
            print(f"ВНИМАНИЕ: Несоответствие между пользователями с ролью 'doctor' ({doctor_count}) и записями в таблице 'doctors' ({doctors_table_count})")
    
    except sqlite3.Error as e:
        print(f"Ошибка при проверке таблицы пользователей: {str(e)}")

def check_appointments_table(cursor):
    """Проверяет таблицу записей на прием и выводит статистику"""
    print("\n[Проверка таблицы записей на прием]")
    
    try:
        # Подсчет записей по статусам
        cursor.execute("SELECT status, COUNT(*) FROM appointments GROUP BY status")
        status_counts = cursor.fetchall()
        
        print("Статистика записей по статусам:")
        for status, count in status_counts:
            print(f"  {status}: {count}")
        
        # Проверка на корректность дат
        cursor.execute("SELECT COUNT(*) FROM appointments WHERE appointment_date IS NULL OR appointment_date = ''")
        invalid_dates = cursor.fetchone()[0]
        
        if invalid_dates > 0:
            print(f"ВНИМАНИЕ: Найдено {invalid_dates} записей с некорректными датами")
    
    except sqlite3.Error as e:
        print(f"Ошибка при проверке таблицы записей на прием: {str(e)}")

def check_and_fix_foreign_keys(cursor, conn):
    """Проверяет и исправляет проблемы с внешними ключами"""
    print("\n[Проверка внешних ключей]")
    
    try:
        # Включение проверки внешних ключей
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Проверка записей на прием с несуществующими пациентами
        cursor.execute("""
            SELECT COUNT(*) FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            WHERE p.id IS NULL
        """)
        invalid_patient_refs = cursor.fetchone()[0]
        
        if invalid_patient_refs > 0:
            print(f"ВНИМАНИЕ: Найдено {invalid_patient_refs} записей с ссылками на несуществующих пациентов")
        
        # Проверка записей на прием с несуществующими врачами
        cursor.execute("""
            SELECT COUNT(*) FROM appointments a
            LEFT JOIN doctors d ON a.doctor_id = d.id
            WHERE d.id IS NULL
        """)
        invalid_doctor_refs = cursor.fetchone()[0]
        
        if invalid_doctor_refs > 0:
            print(f"ВНИМАНИЕ: Найдено {invalid_doctor_refs} записей с ссылками на несуществующих врачей")
    
    except sqlite3.Error as e:
        print(f"Ошибка при проверке внешних ключей: {str(e)}")

def fix_appointment_update_issues(cursor, conn):
    """Исправляет проблемы с обновлением записей на прием"""
    print("\n[Исправление проблем с обновлением записей]")
    
    try:
        # Проверка структуры таблицы appointments
        cursor.execute("PRAGMA table_info(appointments)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Проверка наличия всех необходимых полей
        required_fields = ['id', 'patient_id', 'doctor_id', 'appointment_date', 'appointment_time', 'status', 'notes']
        missing_fields = [field for field in required_fields if field not in column_names]
        
        if missing_fields:
            print(f"Добавление отсутствующих полей в таблицу appointments: {', '.join(missing_fields)}")
            for field in missing_fields:
                if field == 'notes':
                    cursor.execute(f"ALTER TABLE appointments ADD COLUMN {field} TEXT")
                elif field == 'status':
                    cursor.execute(f"ALTER TABLE appointments ADD COLUMN {field} TEXT DEFAULT 'scheduled'")
                else:
                    cursor.execute(f"ALTER TABLE appointments ADD COLUMN {field} TEXT")
            conn.commit()
        
        # Проверка на NULL значения в обязательных полях
        cursor.execute("""
            SELECT id FROM appointments 
            WHERE patient_id IS NULL OR doctor_id IS NULL OR appointment_date IS NULL OR appointment_time IS NULL
        """)
        null_value_records = cursor.fetchall()
        
        if null_value_records:
            print(f"Найдено {len(null_value_records)} записей с NULL значениями в обязательных полях")
            for record_id in null_value_records:
                # Удаление проблемных записей с NULL значениями
                cursor.execute("DELETE FROM appointments WHERE id = ?", (record_id[0],))
            conn.commit()
            print(f"Удалено {len(null_value_records)} проблемных записей")
        
        # Добавление триггера безопасного обновления для таблицы appointments
        print("Добавление триггера для безопасного обновления записей...")
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS safe_appointment_update
        BEFORE UPDATE ON appointments
        BEGIN
            -- Проверка валидности patient_id
            SELECT CASE
                WHEN NEW.patient_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM patients WHERE id = NEW.patient_id)
                THEN RAISE(ABORT, 'Некорректный ID пациента')
            END;
            
            -- Проверка валидности doctor_id
            SELECT CASE
                WHEN NEW.doctor_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM doctors WHERE id = NEW.doctor_id)
                THEN RAISE(ABORT, 'Некорректный ID врача')
            END;
            
            -- Установка значения по умолчанию для status, если NULL
            SELECT CASE
                WHEN NEW.status IS NULL
                THEN NEW.status = 'scheduled'
            END;
        END;
        """)
        conn.commit()
        
        print("Исправления для обновления записей успешно применены")
    
    except sqlite3.Error as e:
        print(f"Ошибка при исправлении проблем с обновлением записей: {str(e)}")

def fix_other_issues(cursor, conn):
    """Исправляет другие потенциальные проблемы с базой данных"""
    print("\n[Исправление других потенциальных проблем]")
    
    try:
        # Очистка пустых строк в полях email и телефон
        cursor.execute("UPDATE patients SET email = NULL WHERE email = ''")
        cursor.execute("UPDATE patients SET phone = NULL WHERE phone = ''")
        conn.commit()
        print("Очищены пустые строки в полях email и телефон")
        
        # Проверка индексов
        cursor.execute("PRAGMA index_list(patients)")
        indices = cursor.fetchall()
        
        if not indices:
            print("Добавление индексов для улучшения производительности...")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(full_name)")
            conn.commit()
            print("Добавлен индекс на столбец full_name в таблице patients")
    
    except sqlite3.Error as e:
        print(f"Ошибка при исправлении других проблем: {str(e)}")

def check_db_integrity(cursor):
    """Проверяет целостность базы данных"""
    print("\n[Проверка целостности базы данных]")
    
    try:
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        
        if result and result[0] == 'ok':
            print("Проверка целостности базы данных пройдена успешно")
        else:
            print(f"ВНИМАНИЕ: Проверка целостности базы данных выявила проблемы: {result}")
    
    except sqlite3.Error as e:
        print(f"Ошибка при проверке целостности базы данных: {str(e)}")

if __name__ == "__main__":
    if check_and_fix_db():
        print("\nБаза данных успешно проверена и исправлена")
        sys.exit(0)
    else:
        print("\nПроизошла ошибка при проверке и исправлении базы данных")
        sys.exit(1) 