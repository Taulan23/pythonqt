from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from qt_material import apply_stylesheet

class LoginWindow(QWidget):
    """Окно авторизации пользователя"""
    
    # Сигнал, который будет отправлен при успешной авторизации
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        """Инициализация интерфейса"""
        # Настройка окна
        self.setWindowTitle('Авторизация - Медицинский центр')
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        
        # Основной макет
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Заголовок
        header_label = QLabel("Авторизация")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # Форма входа
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        
        # Поле логина
        login_layout = QVBoxLayout()
        login_label = QLabel("Логин:")
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_input)
        form_layout.addLayout(login_layout)
        
        # Поле пароля
        password_layout = QVBoxLayout()
        password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)
        
        main_layout.addLayout(form_layout)
        
        # Кнопка входа
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.login_button = QPushButton("Войти")
        self.login_button.setFixedSize(120, 40)
        self.login_button.clicked.connect(self.authenticate)
        button_layout.addWidget(self.login_button)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Установка основного макета
        self.setLayout(main_layout)
        
        # Настройка стиля
        apply_stylesheet(self, theme='light_blue.xml')
    
    def authenticate(self):
        """Проверка логина и пароля"""
        username = self.login_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите логин и пароль")
            return
        
        # Импортируем здесь, чтобы избежать циклических импортов
        from app.database.database import Database
        
        db = Database()
        user_data = db.authenticate_user(username, password)
        
        if user_data:
            # Авторизация успешна, отправляем сигнал
            self.login_successful.emit(user_data)
        else:
            # Авторизация не удалась
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
    
    def keyPressEvent(self, event):
        """Обработка нажатия клавиш"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.authenticate()
        else:
            super().keyPressEvent(event) 