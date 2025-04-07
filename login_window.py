from PySide6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                               QVBoxLayout, QHBoxLayout, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
import sys
import os

from database_connection import db

class LoginWindow(QWidget):
    """Окно авторизации пользователя"""
    # Сигнал для передачи данных о пользователе после успешной авторизации
    login_successful = Signal(dict)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Авторизация - Медицинский центр")
        self.setFixedSize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Заголовок
        title_label = QLabel("Авторизация в системе")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # Поле для ввода логина
        username_layout = QVBoxLayout()
        username_label = QLabel("Логин:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        main_layout.addLayout(username_layout)
        
        # Поле для ввода пароля
        password_layout = QVBoxLayout()
        password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        main_layout.addLayout(password_layout)
        
        # Кнопка входа
        login_button = QPushButton("Войти")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        login_button.clicked.connect(self.authenticate)
        main_layout.addWidget(login_button)
        
        # Настройка нажатия Enter для входа
        self.username_input.returnPressed.connect(login_button.click)
        self.password_input.returnPressed.connect(login_button.click)
        
        # Информация о системе
        info_label = QLabel("Медицинский центр - Система документооборота")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: gray;")
        main_layout.addWidget(info_label)
        
        self.setLayout(main_layout)
        
        # Установка фокуса на поле ввода логина
        self.username_input.setFocus()
        
    def authenticate(self):
        """Проверка логина и пароля пользователя"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
        
        print(f"Попытка входа: логин={username}, пароль={password}")
        
        # Проверка логина и пароля через базу данных
        user = db.authenticate_user(username, password)
        
        if user:
            print(f"Успешная авторизация пользователя: {username}, роль: {user['role']}")
            # Emit the signal with user data
            self.login_successful.emit(user)
        else:
            # Проверяем явно, если пользователь существует в базе данных
            check_user = db.fetch_one("SELECT * FROM users WHERE username = ?", (username,))
            if check_user:
                print(f"Пользователь {username} существует, но пароль неверный. Ожидается: {check_user['password']}")
                QMessageBox.critical(self, "Ошибка аутентификации", 
                                    "Неверный пароль.\nПроверьте введенные данные и попробуйте снова.")
            else:
                print(f"Пользователь {username} не найден в базе данных")
                QMessageBox.critical(self, "Ошибка аутентификации", 
                                    "Пользователь не найден.\nПроверьте введенные данные и попробуйте снова.")
            
            self.password_input.clear()
            self.password_input.setFocus()
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        db.disconnect()
        event.accept()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec()) 