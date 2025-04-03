import sqlite3
import os
import hashlib

def get_db_path():
    """Получить путь к файлу базы данных"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, 'resources', 'medical_center.db')

def hash_password(password):
    """Хеширование пароля для безопасного хранения"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Инициализация базы данных и создание таблиц"""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL
    )
    ''')
    
    # Таблица пациентов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        birth_date TEXT NOT NULL,
        gender TEXT NOT NULL,
        phone_number TEXT,
        email TEXT,
        address TEXT
    )
    ''')
    
    # Таблица типов анализов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    )
    ''')
    
    # Таблица параметров для разных типов анализов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_parameters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_type_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        unit TEXT,
        normal_range_min REAL,
        normal_range_max REAL,
        FOREIGN KEY (analysis_type_id) REFERENCES analysis_types (id)
    )
    ''')
    
    # Таблица результатов анализов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        analysis_type_id INTEGER NOT NULL,
        date_taken TEXT NOT NULL,
        lab_technician_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients (id),
        FOREIGN KEY (analysis_type_id) REFERENCES analysis_types (id),
        FOREIGN KEY (lab_technician_id) REFERENCES users (id)
    )
    ''')
    
    # Таблица значений параметров анализов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parameter_values (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_result_id INTEGER NOT NULL,
        parameter_id INTEGER NOT NULL,
        value REAL NOT NULL,
        FOREIGN KEY (analysis_result_id) REFERENCES analysis_results (id),
        FOREIGN KEY (parameter_id) REFERENCES analysis_parameters (id)
    )
    ''')
    
    # Таблица расписания приемов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        status TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients (id),
        FOREIGN KEY (doctor_id) REFERENCES users (id)
    )
    ''')
    
    # Добавим несколько тестовых пользователей
    # Проверим, есть ли уже пользователи
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # Добавим тестовых пользователей
        users = [
            ('admin', hash_password('admin'), 'admin', 'Администратор'),
            ('doctor', hash_password('doctor'), 'doctor', 'Иванов Иван Иванович'),
            ('lab', hash_password('lab'), 'lab_technician', 'Петров Петр Петрович')
        ]
        
        cursor.executemany(
            "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
            users
        )
        
        # Добавим типы анализов
        analysis_types = [
            ('Общий анализ крови', 'Общий анализ крови (ОАК)'),
            ('Биохимический анализ крови', 'Биохимический анализ крови'),
            ('Общий анализ мочи', 'Общий анализ мочи (ОАМ)')
        ]
        
        cursor.executemany(
            "INSERT INTO analysis_types (name, description) VALUES (?, ?)",
            analysis_types
        )
        
        # Добавим параметры для общего анализа крови
        cursor.execute("SELECT id FROM analysis_types WHERE name = 'Общий анализ крови'")
        blood_analysis_id = cursor.fetchone()[0]
        
        blood_parameters = [
            (blood_analysis_id, 'Лейкоциты', '10^9/л', 4.0, 9.0),
            (blood_analysis_id, 'Эритроциты', '10^12/л', 3.9, 5.0),
            (blood_analysis_id, 'Гемоглобин', 'г/л', 120, 160),
            (blood_analysis_id, 'Тромбоциты', '10^9/л', 180, 320),
            (blood_analysis_id, 'СОЭ', 'мм/ч', 2, 15)
        ]
        
        cursor.executemany(
            "INSERT INTO analysis_parameters (analysis_type_id, name, unit, normal_range_min, normal_range_max) VALUES (?, ?, ?, ?, ?)",
            blood_parameters
        )
        
        # Добавим параметры для биохимического анализа
        cursor.execute("SELECT id FROM analysis_types WHERE name = 'Биохимический анализ крови'")
        biochem_analysis_id = cursor.fetchone()[0]
        
        biochem_parameters = [
            (biochem_analysis_id, 'Глюкоза', 'ммоль/л', 3.9, 6.1),
            (biochem_analysis_id, 'Холестерин общий', 'ммоль/л', 3.5, 5.2),
            (biochem_analysis_id, 'АЛТ', 'Ед/л', 0, 41),
            (biochem_analysis_id, 'АСТ', 'Ед/л', 0, 38),
            (biochem_analysis_id, 'Креатинин', 'мкмоль/л', 62, 115)
        ]
        
        cursor.executemany(
            "INSERT INTO analysis_parameters (analysis_type_id, name, unit, normal_range_min, normal_range_max) VALUES (?, ?, ?, ?, ?)",
            biochem_parameters
        )
        
        # Добавим тестовых пациентов
        patients = [
            ('Сидоров Сидор Сидорович', '1980-05-15', 'Мужской', '+7(999)123-45-67', 'sidorov@mail.ru', 'г. Москва, ул. Пушкина, д. 1'),
            ('Смирнова Анна Ивановна', '1992-10-20', 'Женский', '+7(999)765-43-21', 'smirnova@mail.ru', 'г. Москва, ул. Лермонтова, д. 5')
        ]
        
        cursor.executemany(
            "INSERT INTO patients (full_name, birth_date, gender, phone_number, email, address) VALUES (?, ?, ?, ?, ?, ?)",
            patients
        )
    
    conn.commit()
    conn.close()
    
    print(f"База данных инициализирована: {db_path}")
    
    return db_path

if __name__ == '__main__':
    init_db() 