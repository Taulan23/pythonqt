import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from qt_material import apply_stylesheet

from app.database.schema import init_db
from app.ui.login_window import LoginWindow
from app.ui.lab_technician_window import LabTechnicianWindow
from app.ui.doctor_window import DoctorWindow
from app.ui.admin_window import AdminWindow
from app.models.models import UserRole

class MedicalCenterApp:
    """Главный класс приложения"""
    
    def __init__(self):
        # Инициализация базы данных
        self.db_path = init_db()
        
        # Создание и настройка приложения
        self.app = QApplication(sys.argv)
        
        # Применение стиля материального дизайна
        # Доступные темы: 'light_blue.xml', 'light_cyan.xml', 'light_lightgreen.xml',
        # 'light_pink.xml', 'light_purple.xml', 'light_red.xml', 'light_teal.xml',
        # 'light_yellow.xml', 'dark_amber.xml', 'dark_blue.xml', 'dark_cyan.xml',
        # 'dark_lightgreen.xml', 'dark_pink.xml', 'dark_purple.xml', 'dark_red.xml',
        # 'dark_teal.xml', 'dark_yellow.xml'
        apply_stylesheet(self.app, theme='light_blue.xml')
        
        # Создание и отображение окна авторизации
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.on_login_successful)
        self.login_window.show()
    
    def on_login_successful(self, user_data):
        """Обработка успешной авторизации"""
        self.login_window.hide()
        
        # Определяем, какое окно показать в зависимости от роли пользователя
        if user_data['role'] == UserRole.ADMIN.value:
            self.main_window = AdminWindow(user_data)
        elif user_data['role'] == UserRole.DOCTOR.value:
            self.main_window = DoctorWindow(user_data)
        elif user_data['role'] == UserRole.LAB_TECHNICIAN.value:
            self.main_window = LabTechnicianWindow(user_data)
        else:
            # Если роль неизвестна, показываем окно лаборанта
            self.main_window = LabTechnicianWindow(user_data)
        
        # Показываем основное окно
        self.main_window.show()
    
    def run(self):
        """Запуск приложения"""
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    app = MedicalCenterApp()
    app.run() 