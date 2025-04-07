import sys
from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox
from PySide6.QtCore import QTimer

from login_window import LoginWindow
from lab_technician_window import LabTechnicianWindow
from doctor_window import DoctorWindow
from admin_window import AdminWindow
from database_connection import db

class MedicalCenter:
    """Главный класс приложения"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = None
        self.current_window = None
        
        # Подключение к базе данных
        if self.initialize_database():
            self.start_login()
        else:
            sys.exit(1)
    
    def initialize_database(self):
        """Инициализация подключения к базе данных с запросом пароля"""
        attempts = 3
        while attempts > 0:
            password, ok = QInputDialog.getText(
                None, 
                "Авторизация базы данных", 
                "Введите пароль для доступа к базе данных:",
                QLineEdit.Password
            )
            
            if not ok:
                # Пользователь отменил ввод
                QMessageBox.critical(None, "Ошибка", "Доступ к базе данных необходим для работы приложения")
                return False
            
            if db.connect(password):
                print("Успешное подключение к базе данных")
                return True
            
            attempts -= 1
            if attempts > 0:
                QMessageBox.warning(
                    None, 
                    "Ошибка авторизации", 
                    f"Неверный пароль. Осталось попыток: {attempts}"
                )
            else:
                QMessageBox.critical(
                    None, 
                    "Доступ запрещен", 
                    "Превышено количество попыток ввода пароля"
                )
                return False
    
    def start_login(self):
        """Запуск окна авторизации"""
        if self.current_window:
            self.current_window.close()
        
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.handle_login)
        self.login_window.show()
        self.current_window = self.login_window
    
    def handle_login(self, user_data):
        """Обработка успешной авторизации"""
        print(f"Пользователь {user_data['username']} успешно авторизован. Роль: {user_data['role']}")
        
        # Закрываем окно авторизации
        self.login_window.close()
        
        # Открываем окно соответствующее роли пользователя
        if user_data['role'] == 'lab':
            self.open_lab_technician_window(user_data)
        elif user_data['role'] == 'doctor':
            self.open_doctor_window(user_data)
        elif user_data['role'] == 'admin':
            self.open_admin_window(user_data)
        else:
            print(f"Неизвестная роль: {user_data['role']}")
            # Возвращение к окну авторизации в случае неизвестной роли
            QTimer.singleShot(0, self.start_login)
    
    def open_lab_technician_window(self, user_data):
        """Открытие окна лаборанта"""
        lab_window = LabTechnicianWindow(user_data)
        lab_window.logout_signal.connect(self.start_login)
        lab_window.show()
        self.current_window = lab_window
    
    def open_doctor_window(self, user_data):
        """Открытие окна врача"""
        doctor_window = DoctorWindow(user_data)
        doctor_window.logout_signal.connect(self.start_login)
        doctor_window.show()
        self.current_window = doctor_window
    
    def open_admin_window(self, user_data):
        """Открытие окна администратора"""
        admin_window = AdminWindow(user_data)
        admin_window.logout_signal.connect(self.start_login)
        admin_window.show()
        self.current_window = admin_window
    
    def run(self):
        """Запуск главного цикла приложения"""
        return self.app.exec()


if __name__ == "__main__":
    # Запуск приложения
    medical_center = MedicalCenter()
    sys.exit(medical_center.run()) 