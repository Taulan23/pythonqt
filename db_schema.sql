-- Создание базы данных для медицинского центра
CREATE DATABASE IF NOT EXISTS med_center;
USE med_center;

-- Таблица пользователей системы (администраторы, врачи, лаборанты)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'doctor', 'lab') NOT NULL,
    email VARCHAR(100),
    last_login DATETIME,
    status ENUM('active', 'blocked') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица пациентов
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Таблица типов анализов
CREATE TABLE IF NOT EXISTS analysis_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parameters TEXT -- JSON или сериализованный список параметров анализа
);

-- Таблица результатов анализов
CREATE TABLE IF NOT EXISTS analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    analysis_type_id INT NOT NULL,
    lab_user_id INT NOT NULL,
    result_data TEXT, -- JSON или сериализованные результаты
    result_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'completed', 'sent') DEFAULT 'pending',
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (analysis_type_id) REFERENCES analysis_types(id),
    FOREIGN KEY (lab_user_id) REFERENCES users(id)
);

-- Таблица врачей
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Таблица расписания приемов
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id),
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

-- Вставка тестовых данных

-- Пользователи
INSERT INTO users (username, password, full_name, role, email) VALUES
('admin', 'admin123', 'Администратор Системы', 'admin', 'admin@medcenter.com'),
('doctor1', 'doc123', 'Петров Иван Сергеевич', 'doctor', 'doctor1@medcenter.com'),
('lab1', 'lab123', 'Иванова Мария Петровна', 'lab', 'lab1@medcenter.com');

-- Пациенты
INSERT INTO patients (full_name, birth_date, phone, email, address) VALUES
('Иванов Иван Иванович', '1978-05-15', '+7 (900) 123-45-67', 'ivanov@example.com', 'г. Москва, ул. Ленина, 10-15'),
('Петрова Анна Сергеевна', '1990-10-20', '+7 (900) 987-65-43', 'petrova@example.com', 'г. Москва, пр. Мира, 25-42'),
('Сидоров Петр Николаевич', '1965-03-07', '+7 (900) 111-22-33', 'sidorov@example.com', 'г. Москва, ул. Гагарина, 5-10'),
('Кузнецова Елена Владимировна', '1995-12-18', '+7 (900) 444-55-66', 'kuznetsova@example.com', 'г. Москва, ул. Пушкина, 15-7'),
('Смирнов Алексей Петрович', '1958-07-30', '+7 (900) 777-88-99', 'smirnov@example.com', 'г. Москва, ул. Лермонтова, 20-30');

-- Типы анализов
INSERT INTO analysis_types (name, description, parameters) VALUES
('Общий анализ крови', 'Базовый анализ состава крови', 'Гемоглобин,Эритроциты,Лейкоциты,Тромбоциты,СОЭ'),
('Биохимический анализ крови', 'Анализ биохимических показателей крови', 'Глюкоза,Холестерин,Билирубин,АЛТ,АСТ,Креатинин,Мочевина'),
('Общий анализ мочи', 'Базовый анализ состава мочи', 'Цвет,Прозрачность,pH,Белок,Глюкоза,Кетоновые тела,Лейкоциты,Эритроциты');

-- Врачи (связанные с пользователями)
INSERT INTO doctors (user_id, specialization) VALUES
(2, 'Терапевт');

-- Тестовые записи на прием
INSERT INTO appointments (doctor_id, patient_id, appointment_date, status, notes) VALUES
(1, 1, '2023-10-15 10:00:00', 'scheduled', 'Первичный прием'),
(1, 2, '2023-10-15 11:00:00', 'scheduled', 'Повторный прием'),
(1, 3, '2023-10-16 09:30:00', 'scheduled', 'Консультация по результатам анализов'),
(1, 4, '2023-10-16 10:30:00', 'scheduled', 'Профилактический осмотр'),
(1, 5, '2023-10-17 14:00:00', 'scheduled', 'Контроль лечения'); 