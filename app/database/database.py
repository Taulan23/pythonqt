import sqlite3
from app.database.schema import get_db_path, hash_password

class Database:
    def __init__(self):
        self.db_path = get_db_path()
    
    def _get_connection(self):
        """Получить соединение с базой данных"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query, parameters=(), fetchone=False):
        """Выполнить запрос к базе данных"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        
        result = None
        if query.lstrip().upper().startswith('SELECT'):
            if fetchone:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid
        
        conn.close()
        return result
    
    def authenticate_user(self, username, password):
        """Аутентификация пользователя"""
        hashed_password = hash_password(password)
        query = "SELECT id, username, role, full_name FROM users WHERE username = ? AND password = ?"
        result = self.execute_query(query, (username, hashed_password), fetchone=True)
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'role': result[2],
                'full_name': result[3]
            }
        return None
    
    # Методы для работы с пациентами
    def get_all_patients(self):
        """Получить список всех пациентов"""
        query = "SELECT id, full_name, birth_date, gender, phone_number, email, address FROM patients ORDER BY full_name"
        return self.execute_query(query)
    
    def get_patient(self, patient_id):
        """Получить информацию о пациенте по ID"""
        query = "SELECT id, full_name, birth_date, gender, phone_number, email, address FROM patients WHERE id = ?"
        return self.execute_query(query, (patient_id,), fetchone=True)
    
    def add_patient(self, full_name, birth_date, gender, phone_number, email, address):
        """Добавить нового пациента"""
        query = """
        INSERT INTO patients (full_name, birth_date, gender, phone_number, email, address) 
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (full_name, birth_date, gender, phone_number, email, address))
    
    def update_patient(self, patient_id, full_name, birth_date, gender, phone_number, email, address):
        """Обновить информацию о пациенте"""
        query = """
        UPDATE patients 
        SET full_name = ?, birth_date = ?, gender = ?, phone_number = ?, email = ?, address = ? 
        WHERE id = ?
        """
        self.execute_query(query, (full_name, birth_date, gender, phone_number, email, address, patient_id))
    
    def delete_patient(self, patient_id):
        """Удалить пациента"""
        query = "DELETE FROM patients WHERE id = ?"
        self.execute_query(query, (patient_id,))
    
    # Методы для работы с анализами
    def get_all_analysis_types(self):
        """Получить список всех типов анализов"""
        query = "SELECT id, name, description FROM analysis_types ORDER BY name"
        return self.execute_query(query)
    
    def get_analysis_parameters(self, analysis_type_id):
        """Получить параметры для типа анализа"""
        query = """
        SELECT id, name, unit, normal_range_min, normal_range_max 
        FROM analysis_parameters 
        WHERE analysis_type_id = ? 
        ORDER BY id
        """
        return self.execute_query(query, (analysis_type_id,))
    
    def add_analysis_result(self, patient_id, analysis_type_id, date_taken, lab_technician_id):
        """Добавить новый результат анализа"""
        query = """
        INSERT INTO analysis_results (patient_id, analysis_type_id, date_taken, lab_technician_id, status) 
        VALUES (?, ?, ?, ?, 'новый')
        """
        return self.execute_query(query, (patient_id, analysis_type_id, date_taken, lab_technician_id))
    
    def add_parameter_value(self, analysis_result_id, parameter_id, value):
        """Добавить значение параметра анализа"""
        query = """
        INSERT INTO parameter_values (analysis_result_id, parameter_id, value) 
        VALUES (?, ?, ?)
        """
        return self.execute_query(query, (analysis_result_id, parameter_id, value))
    
    def get_analysis_results(self, patient_id=None, analysis_type_id=None, from_date=None, to_date=None):
        """Получить результаты анализов с фильтрацией"""
        query = """
        SELECT r.id, p.full_name, p.birth_date, t.name, r.date_taken, u.full_name, r.status
        FROM analysis_results r
        JOIN patients p ON r.patient_id = p.id
        JOIN analysis_types t ON r.analysis_type_id = t.id
        JOIN users u ON r.lab_technician_id = u.id
        WHERE 1=1
        """
        params = []
        
        if patient_id:
            query += " AND r.patient_id = ?"
            params.append(patient_id)
        
        if analysis_type_id:
            query += " AND r.analysis_type_id = ?"
            params.append(analysis_type_id)
        
        if from_date:
            query += " AND r.date_taken >= ?"
            params.append(from_date)
        
        if to_date:
            query += " AND r.date_taken <= ?"
            params.append(to_date)
        
        query += " ORDER BY r.date_taken DESC"
        
        return self.execute_query(query, tuple(params))
    
    def get_analysis_result_details(self, analysis_result_id):
        """Получить детали результата анализа"""
        # Получить основную информацию об анализе
        query_main = """
        SELECT r.id, p.id, p.full_name, p.birth_date, t.id, t.name, r.date_taken, u.full_name, r.status
        FROM analysis_results r
        JOIN patients p ON r.patient_id = p.id
        JOIN analysis_types t ON r.analysis_type_id = t.id
        JOIN users u ON r.lab_technician_id = u.id
        WHERE r.id = ?
        """
        main_info = self.execute_query(query_main, (analysis_result_id,), fetchone=True)
        
        if not main_info:
            return None
        
        # Получить значения параметров
        query_values = """
        SELECT ap.id, ap.name, ap.unit, ap.normal_range_min, ap.normal_range_max, pv.value
        FROM parameter_values pv
        JOIN analysis_parameters ap ON pv.parameter_id = ap.id
        WHERE pv.analysis_result_id = ?
        ORDER BY ap.id
        """
        values = self.execute_query(query_values, (analysis_result_id,))
        
        return {
            'id': main_info[0],
            'patient': {
                'id': main_info[1],
                'full_name': main_info[2],
                'birth_date': main_info[3]
            },
            'analysis_type': {
                'id': main_info[4],
                'name': main_info[5]
            },
            'date_taken': main_info[6],
            'lab_technician': main_info[7],
            'status': main_info[8],
            'parameters': [
                {
                    'id': v[0],
                    'name': v[1],
                    'unit': v[2],
                    'normal_min': v[3],
                    'normal_max': v[4],
                    'value': v[5],
                    'is_normal': v[3] <= v[5] <= v[4] if v[3] is not None and v[4] is not None else None
                }
                for v in values
            ]
        }
    
    # Методы для работы с расписанием
    def get_appointments(self, doctor_id=None, patient_id=None, from_date=None, to_date=None):
        """Получить список приемов с фильтрацией"""
        query = """
        SELECT a.id, p.id, p.full_name, u.id, u.full_name, a.appointment_date, a.appointment_time, a.status, a.notes
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN users u ON a.doctor_id = u.id
        WHERE 1=1
        """
        params = []
        
        if doctor_id:
            query += " AND a.doctor_id = ?"
            params.append(doctor_id)
        
        if patient_id:
            query += " AND a.patient_id = ?"
            params.append(patient_id)
        
        if from_date:
            query += " AND a.appointment_date >= ?"
            params.append(from_date)
        
        if to_date:
            query += " AND a.appointment_date <= ?"
            params.append(to_date)
        
        query += " ORDER BY a.appointment_date, a.appointment_time"
        
        return self.execute_query(query, tuple(params))
    
    def add_appointment(self, patient_id, doctor_id, appointment_date, appointment_time, status="запланирован", notes=None):
        """Добавить новый прием"""
        query = """
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, notes) 
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (patient_id, doctor_id, appointment_date, appointment_time, status, notes))
    
    def update_appointment_status(self, appointment_id, status, notes=None):
        """Обновить статус приема"""
        query = """
        UPDATE appointments 
        SET status = ?, notes = ? 
        WHERE id = ?
        """
        self.execute_query(query, (status, notes, appointment_id))
    
    def get_doctors(self):
        """Получить список врачей"""
        query = "SELECT id, username, full_name FROM users WHERE role = 'doctor' ORDER BY full_name"
        return self.execute_query(query) 