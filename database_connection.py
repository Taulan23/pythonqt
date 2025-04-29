import json
import os
import sqlite3
import hashlib
from datetime import datetime

class DatabaseConnection:
    """Класс для работы с базой данных SQLite"""
    _instance = None
    _db_password = "1"  # Пароль для доступа к базе данных
    
    def __new__(cls):
        """Реализация паттерна Singleton для подключения к БД"""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connection = None
        return cls._instance
    
    def __init__(self):
        """Инициализация подключения к БД"""
        self.db_path = 'med_center.db'
        self.authorized = False
        
        # Статус подключения
        self.connected = False
    
    def verify_password(self, password):
        """Проверка пароля для доступа к базе данных"""
        return password == self._db_password
    
    def connect(self, password=None):
        """Установка соединения с базой данных"""
        # Проверка пароля при первом подключении
        if not self.authorized and password is not None:
            if not self.verify_password(password):
                print("Неверный пароль для доступа к базе данных")
                return False
            self.authorized = True
        
        # Если уже авторизованы или пароль верный
        if self.authorized:
            try:
                # Проверка существования файла базы данных
                db_exists = os.path.exists(self.db_path)
                print(f"Файл базы данных {'существует' if db_exists else 'не существует'}")
                
                if self._connection is None:
                    self._connection = sqlite3.connect(self.db_path)
                    self._connection.row_factory = self._dict_factory
                    self.connected = True
                    print("Подключение к базе данных установлено")
                    
                    # Создаем таблицы если они не существуют
                    self._initialize_database()
                    
                    # Если файл базы данных не существовал, то создаем тестовые данные
                    if not db_exists:
                        print("Создание тестовых данных...")
                        self._create_test_data(force=True)
                return True
            except sqlite3.Error as e:
                self.connected = False
                print(f"Ошибка подключения к базе данных: {e}")
                return False
        else:
            print("Необходима авторизация для доступа к базе данных")
            return False
    
    def _dict_factory(self, cursor, row):
        """Конвертирует строку результата в словарь"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    def _initialize_database(self):
        """Инициализация базы данных (создание таблиц)"""
        try:
            cursor = self._connection.cursor()
            
            # Таблица пользователей
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'lab')),
                email TEXT,
                last_login TEXT,
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'blocked')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Таблица пациентов
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                gender TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Таблица типов анализов
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                parameters TEXT
            )
            ''')
            
            # Таблица результатов анализов
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                analysis_type_id INTEGER NOT NULL,
                lab_user_id INTEGER NOT NULL,
                result_data TEXT,
                result_date TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'sent')),
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (analysis_type_id) REFERENCES analysis_types(id),
                FOREIGN KEY (lab_user_id) REFERENCES users(id)
            )
            ''')
            
            # Таблица врачей
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                specialization TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            ''')
            
            # Таблица расписания приемов
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER NOT NULL,
                patient_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'completed', 'cancelled')),
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id),
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
            ''')
            
            # Создаем тестовые данные, если таблицы были пустыми
            self._create_test_data()
            
            self._connection.commit()
            
        except sqlite3.Error as e:
            print(f"Ошибка при инициализации базы данных: {e}")
            self._connection.rollback()
    
    def _create_test_data(self, force=False):
        """Создание тестовых данных, если они не существуют"""
        # Проверяем, есть ли пользователи
        cur = self._connection.cursor()
        cur.execute("SELECT COUNT(*) as count FROM users")
        result = cur.fetchone()
        
        if result and result['count'] == 0 or force:
            # Создаем пользователей
            user_data = [
                ('admin', 'admin123', 'Администратор Системы', 'admin', 'admin@medcenter.com'),
                ('doctor1', 'doc123', 'Петров Иван Сергеевич', 'doctor', 'doctor1@medcenter.com'),
                ('lab1', 'lab123', 'Иванова Мария Петровна', 'lab', 'lab1@medcenter.com'),
                ('lab2', '1', 'Смирнова Елена Алексеевна', 'lab', 'lab2@medcenter.com')
            ]
            
            cur.executemany(
                "INSERT INTO users (username, password, full_name, role, email) VALUES (?, ?, ?, ?, ?)",
                user_data
            )
            
            # Создаем пациентов
            patient_data = [
                ('Иванов Иван Иванович', '1978-05-15', '+7 (900) 123-45-67', 'ivanov@example.com', 'г. Москва, ул. Ленина, 10-15'),
                ('Петрова Анна Сергеевна', '1990-10-20', '+7 (900) 987-65-43', 'petrova@example.com', 'г. Москва, пр. Мира, 25-42'),
                ('Сидоров Петр Николаевич', '1965-03-07', '+7 (900) 111-22-33', 'sidorov@example.com', 'г. Москва, ул. Гагарина, 5-10'),
                ('Кузнецова Елена Владимировна', '1995-12-18', '+7 (900) 444-55-66', 'kuznetsova@example.com', 'г. Москва, ул. Пушкина, 15-7'),
                ('Смирнов Алексей Петрович', '1958-07-30', '+7 (900) 777-88-99', 'smirnov@example.com', 'г. Москва, ул. Лермонтова, 20-30')
            ]
            
            cur.executemany(
                "INSERT INTO patients (full_name, birth_date, phone, email, address) VALUES (?, ?, ?, ?, ?)",
                patient_data
            )
            
            # Создаем типы анализов
            analysis_types_data = [
                ('Общий анализ крови', 'Базовый анализ состава крови', 'Гемоглобин,Эритроциты,Лейкоциты,Тромбоциты,СОЭ'),
                ('Биохимический анализ крови', 'Анализ биохимических показателей крови', 'Глюкоза,Холестерин,Билирубин,АЛТ,АСТ,Креатинин,Мочевина'),
                ('Общий анализ мочи', 'Базовый анализ состава мочи', 'Цвет,Прозрачность,pH,Белок,Глюкоза,Кетоновые тела,Лейкоциты,Эритроциты')
            ]
            
            cur.executemany(
                "INSERT INTO analysis_types (name, description, parameters) VALUES (?, ?, ?)",
                analysis_types_data
            )
            
            # Создаем запись врача для doctor1
            cur.execute("SELECT id FROM users WHERE username = 'doctor1'")
            doctor_user = cur.fetchone()
            
            if doctor_user:
                cur.execute(
                    "INSERT INTO doctors (user_id, specialization) VALUES (?, ?)",
                    (doctor_user['id'], 'Терапевт')
                )
                
                # Получаем ID врача
                cur.execute("SELECT id FROM doctors ORDER BY id DESC LIMIT 1")
                doctor = cur.fetchone()
                
                if doctor:
                    # Создаем записи на прием
                    appointments_data = [
                        (doctor['id'], 1, '2023-10-15 10:00:00', 'scheduled', 'Первичный прием'),
                        (doctor['id'], 2, '2023-10-15 11:00:00', 'scheduled', 'Повторный прием'),
                        (doctor['id'], 3, '2023-10-16 09:30:00', 'scheduled', 'Консультация по результатам анализов'),
                        (doctor['id'], 4, '2023-10-16 10:30:00', 'scheduled', 'Профилактический осмотр'),
                        (doctor['id'], 5, '2023-10-17 14:00:00', 'scheduled', 'Контроль лечения')
                    ]
                    
                    cur.executemany(
                        "INSERT INTO appointments (doctor_id, patient_id, appointment_date, status, notes) VALUES (?, ?, ?, ?, ?)",
                        appointments_data
                    )
            
            # Создаем тестовые результаты анализов для лаборанта lab1
            # Получаем ID лаборанта
            cur.execute("SELECT id FROM users WHERE username = 'lab1'")
            lab_user = cur.fetchone()
            
            if lab_user:
                # Получаем ID типов анализов
                cur.execute("SELECT id FROM analysis_types WHERE name = 'Общий анализ крови'")
                blood_analysis = cur.fetchone()
                
                cur.execute("SELECT id FROM analysis_types WHERE name = 'Биохимический анализ крови'")
                biochem_analysis = cur.fetchone()
                
                cur.execute("SELECT id FROM analysis_types WHERE name = 'Общий анализ мочи'")
                urine_analysis = cur.fetchone()
                
                # Создаем данные результатов анализов
                if blood_analysis and biochem_analysis and urine_analysis:
                    # Тестовые данные анализов для разных пациентов
                    analysis_results_data = [
                        # Общий анализ крови для пациента 1
                        (1, blood_analysis['id'], lab_user['id'], '2023-10-10 09:30:00', '{"Гемоглобин":"140 г/л","Эритроциты":"4.5 млн/мкл","Лейкоциты":"6.8 тыс/мкл","Тромбоциты":"250 тыс/мкл","СОЭ":"10 мм/ч"}', 'completed'),
                        # Биохимический анализ крови для пациента 1
                        (1, biochem_analysis['id'], lab_user['id'], '2023-10-10 10:00:00', '{"Глюкоза":"5.2 ммоль/л","Холестерин":"4.8 ммоль/л","Билирубин":"12 мкмоль/л","АЛТ":"25 Ед/л","АСТ":"22 Ед/л","Креатинин":"80 мкмоль/л","Мочевина":"5.5 ммоль/л"}', 'completed'),
                        # Общий анализ мочи для пациента 1
                        (1, urine_analysis['id'], lab_user['id'], '2023-10-10 10:30:00', '{"Цвет":"Желтый","Прозрачность":"Прозрачная","pH":"6.0","Белок":"Отрицательно","Глюкоза":"Отрицательно","Кетоновые тела":"Отрицательно","Лейкоциты":"0-1 в п/зр","Эритроциты":"0-1 в п/зр"}', 'completed'),
                        
                        # Общий анализ крови для пациента 2
                        (2, blood_analysis['id'], lab_user['id'], '2023-10-11 09:00:00', '{"Гемоглобин":"135 г/л","Эритроциты":"4.2 млн/мкл","Лейкоциты":"7.5 тыс/мкл","Тромбоциты":"220 тыс/мкл","СОЭ":"15 мм/ч"}', 'completed'),
                        
                        # Общий анализ крови для пациента 3
                        (3, blood_analysis['id'], lab_user['id'], '2023-10-12 11:00:00', '{"Гемоглобин":"150 г/л","Эритроциты":"4.7 млн/мкл","Лейкоциты":"5.9 тыс/мкл","Тромбоциты":"280 тыс/мкл","СОЭ":"8 мм/ч"}', 'completed'),
                        
                        # Биохимический анализ крови для пациента 4
                        (4, biochem_analysis['id'], lab_user['id'], '2023-10-13 10:15:00', '{"Глюкоза":"5.5 ммоль/л","Холестерин":"5.2 ммоль/л","Билирубин":"14 мкмоль/л","АЛТ":"28 Ед/л","АСТ":"25 Ед/л","Креатинин":"85 мкмоль/л","Мочевина":"5.8 ммоль/л"}', 'completed'),
                        
                        # Общий анализ мочи для пациента 5
                        (5, urine_analysis['id'], lab_user['id'], '2023-10-14 09:45:00', '{"Цвет":"Соломенно-желтый","Прозрачность":"Прозрачная","pH":"5.8","Белок":"Отрицательно","Глюкоза":"Отрицательно","Кетоновые тела":"Отрицательно","Лейкоциты":"0-2 в п/зр","Эритроциты":"0 в п/зр"}', 'completed')
                    ]
                    
                    cur.executemany(
                        "INSERT INTO analysis_results (patient_id, analysis_type_id, lab_user_id, result_date, result_data, status) VALUES (?, ?, ?, ?, ?, ?)",
                        analysis_results_data
                    )
            
            # Создаем тестовые результаты анализов для лаборанта lab2
            cur.execute("SELECT id FROM users WHERE username = 'lab2'")
            lab_user2 = cur.fetchone()
            
            if lab_user2:
                # Получаем ID типов анализов (повторно использовать уже полученные переменные)
                if not blood_analysis:
                    cur.execute("SELECT id FROM analysis_types WHERE name = 'Общий анализ крови'")
                    blood_analysis = cur.fetchone()
                
                if not biochem_analysis:
                    cur.execute("SELECT id FROM analysis_types WHERE name = 'Биохимический анализ крови'")
                    biochem_analysis = cur.fetchone()
                
                if not urine_analysis:
                    cur.execute("SELECT id FROM analysis_types WHERE name = 'Общий анализ мочи'")
                    urine_analysis = cur.fetchone()
                
                # Создаем данные результатов анализов для лаборанта lab2
                if blood_analysis and biochem_analysis and urine_analysis:
                    # Тестовые данные анализов для разных пациентов
                    lab2_analysis_results_data = [
                        # Общий анализ крови для пациента 3
                        (3, blood_analysis['id'], lab_user2['id'], '2023-10-15 09:30:00', '{"Гемоглобин":"145 г/л","Эритроциты":"4.6 млн/мкл","Лейкоциты":"6.5 тыс/мкл","Тромбоциты":"260 тыс/мкл","СОЭ":"9 мм/ч"}', 'completed'),
                        
                        # Биохимический анализ крови для пациента 2
                        (2, biochem_analysis['id'], lab_user2['id'], '2023-10-15 10:45:00', '{"Глюкоза":"5.1 ммоль/л","Холестерин":"4.9 ммоль/л","Билирубин":"11 мкмоль/л","АЛТ":"24 Ед/л","АСТ":"21 Ед/л","Креатинин":"79 мкмоль/л","Мочевина":"5.3 ммоль/л"}', 'completed'),
                        
                        # Общий анализ мочи для пациента 4
                        (4, urine_analysis['id'], lab_user2['id'], '2023-10-16 11:30:00', '{"Цвет":"Светло-желтый","Прозрачность":"Прозрачная","pH":"6.2","Белок":"Отрицательно","Глюкоза":"Отрицательно","Кетоновые тела":"Отрицательно","Лейкоциты":"0-1 в п/зр","Эритроциты":"0 в п/зр"}', 'completed'),
                        
                        # Общий анализ крови для пациента 5
                        (5, blood_analysis['id'], lab_user2['id'], '2023-10-17 09:15:00', '{"Гемоглобин":"142 г/л","Эритроциты":"4.4 млн/мкл","Лейкоциты":"7.0 тыс/мкл","Тромбоциты":"245 тыс/мкл","СОЭ":"12 мм/ч"}', 'completed')
                    ]
                    
                    cur.executemany(
                        "INSERT INTO analysis_results (patient_id, analysis_type_id, lab_user_id, result_date, result_data, status) VALUES (?, ?, ?, ?, ?, ?)",
                        lab2_analysis_results_data
                    )
            
            self._connection.commit()
    
    def disconnect(self):
        """Закрытие соединения с базой данных"""
        if self._connection:
            self._connection.close()
            self._connection = None
            self.connected = False
            print("Соединение с базой данных закрыто")
    
    def execute_query(self, query, params=None):
        """Выполнение SQL-запроса"""
        if not self.connect():
            return None
            
        try:
            cursor = self._connection.cursor()
            print(f"Выполнение запроса: {query}")
            print(f"Параметры: {params}")
            cursor.execute(query, params or ())
            self._connection.commit()
            # Для INSERT возвращаем lastrowid, для UPDATE/DELETE возвращаем rowcount
            cmd = query.strip().split()[0].lower()
            if cmd == 'insert':
                return cursor.lastrowid
            else:
                return cursor.rowcount
        except sqlite3.Error as e:
            self._connection.rollback()
            print(f"Ошибка выполнения запроса: {e}")
            print(f"Запрос: {query}")
            print(f"Параметры: {params}")
            return None
    
    def fetch_one(self, query, params=None):
        """Получение одной записи из базы данных"""
        if not self.connect():
            return None
            
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None
    
    def fetch_all(self, query, params=None):
        """Получение всех записей из базы данных"""
        if not self.connect():
            return []
            
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return []

    # Методы для работы с пользователями
    def authenticate_user(self, username, password):
        """Аутентификация пользователя"""
        print(f"Попытка аутентификации пользователя: {username}")
        query = "SELECT * FROM users WHERE username = ? AND password = ? AND status = 'active'"
        print(f"Выполнение запроса: {query} с параметрами: {username}, {password}")
        
        # Сначала проверим, есть ли такой пользователь вообще
        check_user = self.fetch_one("SELECT * FROM users WHERE username = ?", (username,))
        if not check_user:
            print(f"Пользователь с логином {username} не найден в базе данных")
            return None
        
        user = self.fetch_one(query, (username, password))
        
        if user:
            print(f"Пользователь {username} успешно аутентифицирован")
            # Обновление времени последнего входа
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_query = "UPDATE users SET last_login = ? WHERE id = ?"
            self.execute_query(update_query, (current_time, user['id']))
            return user
        else:
            print(f"Неверный пароль для пользователя {username}")
            return None
    
    def get_all_users(self):
        """Получение всех пользователей"""
        query = "SELECT * FROM users"
        return self.fetch_all(query)
    
    def add_user(self, username, password, full_name, role, email=None):
        """Добавление нового пользователя"""
        query = """
        INSERT INTO users (username, password, full_name, role, email) 
        VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (username, password, full_name, role, email))
    
    # Методы для работы с пациентами
    def get_all_patients(self):
        """Получение всех пациентов"""
        query = "SELECT * FROM patients"
        return self.fetch_all(query)
    
    def get_patient(self, patient_id):
        """Получение данных о конкретном пациенте"""
        query = "SELECT * FROM patients WHERE id = ?"
        return self.fetch_one(query, (patient_id,))
    
    def add_patient(self, full_name, birth_date, gender=None, phone=None, email=None, address=None):
        """Добавление нового пациента"""
        query = """
        INSERT INTO patients (full_name, birth_date, gender, phone, email, address) 
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (full_name, birth_date, gender, phone, email, address))
    
    def update_patient(self, patient_id, full_name, birth_date, gender=None, phone=None, email=None, address=None):
        """Обновление данных пациента"""
        query = """
        UPDATE patients 
        SET full_name = ?, birth_date = ?, gender = ?, phone = ?, email = ?, address = ? 
        WHERE id = ?
        """
        return self.execute_query(query, (full_name, birth_date, gender, phone, email, address, patient_id))
    
    def delete_patient(self, patient_id):
        """Удаление пациента"""
        query = "DELETE FROM patients WHERE id = ?"
        return self.execute_query(query, (patient_id,))
    
    # Методы для работы с анализами
    def get_all_analysis_types(self):
        """Получение всех типов анализов"""
        query = "SELECT * FROM analysis_types"
        return self.fetch_all(query)
    
    def get_analysis_type(self, analysis_id):
        """Получение информации о конкретном типе анализа"""
        query = "SELECT * FROM analysis_types WHERE id = ?"
        return self.fetch_one(query, (analysis_id,))
    
    def get_analysis_parameters(self, analysis_id):
        """Получение параметров анализа"""
        analysis = self.get_analysis_type(analysis_id)
        if analysis and analysis['parameters']:
            return analysis['parameters'].split(',')
        return []
    
    def add_analysis_result(self, patient_id, analysis_type_id, lab_user_id, result_data):
        """Добавление результата анализа"""
        # Сериализация результатов в строку
        if isinstance(result_data, dict):
            result_data = json.dumps(result_data)
            
        query = """
        INSERT INTO analysis_results (patient_id, analysis_type_id, lab_user_id, result_data, status) 
        VALUES (?, ?, ?, ?, 'completed')
        """
        return self.execute_query(query, (patient_id, analysis_type_id, lab_user_id, result_data))
    
    def get_patient_analysis_results(self, patient_id):
        """Получение всех результатов анализов пациента"""
        query = """
        SELECT ar.*, at.name as analysis_name, p.full_name as patient_name, u.full_name as lab_technician_name 
        FROM analysis_results ar
        JOIN analysis_types at ON ar.analysis_type_id = at.id
        JOIN patients p ON ar.patient_id = p.id
        JOIN users u ON ar.lab_user_id = u.id
        WHERE ar.patient_id = ?
        ORDER BY ar.result_date DESC
        """
        return self.fetch_all(query, (patient_id,))
    
    def get_all_analysis_results(self):
        """Получение всех результатов анализов"""
        query = """
        SELECT ar.*, at.name as analysis_name, p.full_name as patient_name, u.full_name as lab_technician_name 
        FROM analysis_results ar
        JOIN analysis_types at ON ar.analysis_type_id = at.id
        JOIN patients p ON ar.patient_id = p.id
        JOIN users u ON ar.lab_user_id = u.id
        ORDER BY ar.result_date DESC
        """
        return self.fetch_all(query)
    
    # Методы для работы с расписанием
    def get_doctor_schedule(self, doctor_id):
        """Получение расписания врача"""
        query = """
        SELECT a.*, p.full_name as patient_name 
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.doctor_id = ?
        ORDER BY a.appointment_date
        """
        return self.fetch_all(query, (doctor_id,))
    
    def get_all_appointments(self):
        """Получение всех записей на прием"""
        query = """
        SELECT a.*, p.full_name as patient_name, 
               d.specialization as doctor_specialization,
               u.full_name as doctor_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        ORDER BY a.appointment_date
        """
        return self.fetch_all(query)
    
    def add_appointment(self, doctor_id, patient_id, appointment_date, notes=None):
        """Добавление записи на прием"""
        query = """
        INSERT INTO appointments (doctor_id, patient_id, appointment_date, notes) 
        VALUES (?, ?, ?, ?)
        """
        return self.execute_query(query, (doctor_id, patient_id, appointment_date, notes))
    
    def update_appointment_status(self, appointment_id, status):
        """Обновление статуса записи на прием"""
        query = "UPDATE appointments SET status = ? WHERE id = ?"
        return self.execute_query(query, (status, appointment_id))
    
    def get_doctor_by_user_id(self, user_id):
        """Получение информации о враче по ID пользователя"""
        print(f"Получение информации о враче для пользователя с ID: {user_id}")
        query = "SELECT * FROM doctors WHERE user_id = ?"
        result = self.fetch_one(query, (user_id,))
        print(f"Результат запроса информации о враче: {result}")
        return result
    
    def get_patients_without_analysis(self, analysis_type_id=None):
        """Получение списка пациентов, у которых нет анализов определенного типа
        
        Если analysis_type_id не указан, возвращает пациентов, у которых нет анализов вообще.
        """
        if analysis_type_id:
            query = """
            SELECT p.* FROM patients p
            WHERE p.id NOT IN (
                SELECT DISTINCT patient_id FROM analysis_results 
                WHERE analysis_type_id = ?
            )
            ORDER BY p.full_name
            """
            return self.fetch_all(query, (analysis_type_id,))
        else:
            query = """
            SELECT p.* FROM patients p
            WHERE p.id NOT IN (
                SELECT DISTINCT patient_id FROM analysis_results
            )
            ORDER BY p.full_name
            """
            return self.fetch_all(query)

    def get_analysis_result_details(self, result_id):
        """
        Получение детальной информации о результате анализа
        
        :param result_id: ID результата анализа
        :return: Словарь с детальной информацией о результате или None, если результат не найден
        """
        try:
            # Получаем основную информацию о результате анализа
            query = """
            SELECT ar.id, ar.patient_id, ar.analysis_type_id, ar.lab_user_id, 
                   ar.result_data, ar.result_date, ar.status,
                   p.full_name as patient_name, p.birth_date,
                   at.name as analysis_type_name, at.description as analysis_type_description,
                   at.parameters as analysis_type_parameters,
                   u.full_name as lab_technician_name
            FROM analysis_results ar
            JOIN patients p ON ar.patient_id = p.id
            JOIN analysis_types at ON ar.analysis_type_id = at.id
            JOIN users u ON ar.lab_user_id = u.id
            WHERE ar.id = ?
            """
            result = self.fetch_one(query, (result_id,))
            
            if not result:
                return None
            
            # Формируем структуру данных для ответа
            result_details = {
                'id': result['id'],
                'date_taken': result['result_date'],
                'status': result['status'],
                'patient': {
                    'id': result['patient_id'],
                    'full_name': result['patient_name'],
                    'birth_date': result['birth_date'],
                    'gender': 'Не указан'  # Используем значение по умолчанию
                },
                'analysis_type': {
                    'id': result['analysis_type_id'],
                    'name': result['analysis_type_name'],
                    'description': result['analysis_type_description']
                },
                'lab_technician': result['lab_technician_name']
            }
            
            # Получаем и парсим данные результатов
            result_data = result['result_data']
            parameters = []
            
            try:
                # Пробуем разобрать JSON
                import json
                result_data_dict = json.loads(result_data)
                
                # Получаем список параметров анализа
                analysis_parameters = result['analysis_type_parameters'].split(',') if result['analysis_type_parameters'] else []
                
                # Нормальные значения для известных параметров
                normal_values = {
                    'Гемоглобин': {'min': 120, 'max': 160, 'unit': 'г/л'},
                    'Эритроциты': {'min': 3.8, 'max': 5.5, 'unit': 'млн/мкл'},
                    'Лейкоциты': {'min': 4.0, 'max': 9.0, 'unit': 'тыс/мкл'},
                    'Тромбоциты': {'min': 180, 'max': 320, 'unit': 'тыс/мкл'},
                    'СОЭ': {'min': 2, 'max': 15, 'unit': 'мм/ч'},
                    'Глюкоза': {'min': 3.9, 'max': 6.1, 'unit': 'ммоль/л'},
                    'Холестерин': {'min': 3.0, 'max': 5.2, 'unit': 'ммоль/л'},
                    'Билирубин': {'min': 3.4, 'max': 17.1, 'unit': 'мкмоль/л'},
                    'АЛТ': {'min': 5, 'max': 40, 'unit': 'ед/л'},
                    'АСТ': {'min': 5, 'max': 40, 'unit': 'ед/л'},
                    'Креатинин': {'min': 53, 'max': 106, 'unit': 'мкмоль/л'},
                    'Мочевина': {'min': 2.5, 'max': 8.3, 'unit': 'ммоль/л'},
                    'pH': {'min': 5.0, 'max': 7.0, 'unit': ''},
                    'Белок': {'min': None, 'max': None, 'unit': ''},
                    'Кетоновые тела': {'min': None, 'max': None, 'unit': ''}
                }
                
                for param_name in analysis_parameters:
                    param_value = result_data_dict.get(param_name, 'Нет данных')
                    normal_vals = normal_values.get(param_name, {'min': None, 'max': None, 'unit': ''})
                    
                    # Определяем, в норме ли значение
                    is_normal = None
                    if normal_vals['min'] is not None and normal_vals['max'] is not None and isinstance(param_value, (int, float)):
                        is_normal = normal_vals['min'] <= param_value <= normal_vals['max']
                    
                    parameters.append({
                        'name': param_name,
                        'value': param_value,
                        'unit': normal_vals['unit'],
                        'normal_min': normal_vals['min'],
                        'normal_max': normal_vals['max'],
                        'is_normal': is_normal
                    })
                
            except (json.JSONDecodeError, AttributeError, TypeError) as e:
                # Если не удалось разобрать JSON, добавляем результат как текст
                parameters.append({
                    'name': 'Результат',
                    'value': result_data,
                    'unit': '',
                    'normal_min': None,
                    'normal_max': None,
                    'is_normal': None
                })
            
            result_details['parameters'] = parameters
            return result_details
            
        except Exception as e:
            print(f"Ошибка при получении деталей результата анализа: {e}")
            return None


# Создание экземпляра для использования в других модулях
db = DatabaseConnection() 