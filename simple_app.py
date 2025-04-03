#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
                             QLineEdit, QFormLayout, QDialog, QDateEdit, QSpinBox, QComboBox, QTabWidget, QMenu, QInputDialog)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QPalette, QColor, QCursor
import xlwt
import csv
import io

# Тестовые данные пациентов
SAMPLE_PATIENTS = [
    {"id": 1, "name": "Иванов Иван", "age": 45, "diagnosis": "Грипп", "date": "2024-03-27", "status": "На лечении"},
    {"id": 2, "name": "Петрова Анна", "age": 32, "diagnosis": "ОРВИ", "date": "2024-03-26", "status": "Выписан"},
    {"id": 3, "name": "Сидоров Петр", "age": 28, "diagnosis": "Бронхит", "date": "2024-03-25", "status": "На лечении"},
    {"id": 4, "name": "Козлов Михаил", "age": 52, "diagnosis": "Пневмония", "date": "2024-03-24", "status": "На лечении"},
    {"id": 5, "name": "Морозова Елена", "age": 29, "diagnosis": "Ангина", "date": "2024-03-23", "status": "Выписан"},
    {"id": 6, "name": "Новиков Артем", "age": 41, "diagnosis": "Бронхит", "date": "2024-03-22", "status": "На лечении"}
]

# Тестовые данные пользователей
USERS = [
    {
        "username": "admin",
        "password": "admin123",
        "role": "Администратор",
        "full_name": "Администратор Системы",
        "last_login": "2024-03-27",
        "status": "Активен"
    },
    {
        "username": "doctor1",
        "password": "doc123",
        "role": "Врач",
        "full_name": "Петров Иван Сергеевич",
        "last_login": "2024-03-26",
        "status": "Активен"
    },
    {
        "username": "nurse1",
        "password": "nurse123",
        "role": "Медсестра",
        "full_name": "Иванова Мария Петровна",
        "last_login": "2024-03-25",
        "status": "Активен"
    }
]

# Права доступа для разных ролей
ROLE_PERMISSIONS = {
    "Администратор": [
        "view_patients", "add_patient", "edit_patient", "delete_patient",
        "create_report", "manage_users", "view_all_documents",
        "create_medical_report", "create_prescription", "create_sick_leave",
        "view_statistics", "export_data"
    ],
    "Врач": [
        "view_patients", "add_patient", "edit_patient",
        "create_medical_report", "create_prescription", "create_sick_leave",
        "view_own_documents", "create_report"
    ],
    "Медсестра": [
        "view_patients", "add_patient",
        "create_medical_report", "view_own_documents"
    ]
}

class StyleHelper:
    @staticmethod
    def get_main_style():
        return """
            QMainWindow, QDialog {
                background-color: white;
            }
            QLabel {
                color: black;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                gridline-color: #ecf0f1;
                color: black;
            }
            QTableWidget::item {
                padding: 8px;
                color: black;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QLineEdit, QDateEdit, QSpinBox, QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                color: black;
                font-size: 14px;
            }
            QLineEdit:focus, QDateEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            QLabel#statsLabel {
                background-color: #f8f9fa;
                padding: 12px 20px;
                border-radius: 6px;
                border: 1px solid #dee2e6;
                color: black;
                font-weight: bold;
            }
        """

class AddPatientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление пациента")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(15)

        # Поля ввода
        self.name_edit = QLineEdit()
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 120)
        self.diagnosis_edit = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.status_combo = QComboBox()
        self.status_combo.addItems(["На лечении", "Выписан"])

        # Добавляем поля в форму
        layout.addRow("ФИО:", self.name_edit)
        layout.addRow("Возраст:", self.age_spin)
        layout.addRow("Диагноз:", self.diagnosis_edit)
        layout.addRow("Дата:", self.date_edit)
        layout.addRow("Статус:", self.status_combo)

        # Кнопки
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)

    def get_patient_data(self):
        return {
            "name": self.name_edit.text(),
            "age": self.age_spin.value(),
            "diagnosis": self.diagnosis_edit.text(),
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "status": self.status_combo.currentText()
        }

class DocumentTemplate:
    """Шаблоны медицинских документов"""
    TEMPLATES = {
        "medical_report": {
            "name": "Медицинский отчет",
            "fields": ["patient_name", "diagnosis", "treatment", "doctor_name", "date"],
            "allowed_roles": ["Администратор", "Врач", "Медсестра"]
        },
        "prescription": {
            "name": "Рецепт",
            "fields": ["patient_name", "medications", "dosage", "period", "doctor_name", "date"],
            "allowed_roles": ["Администратор", "Врач"]
        },
        "sick_leave": {
            "name": "Больничный лист",
            "fields": ["patient_name", "diagnosis", "start_date", "end_date", "doctor_name"],
            "allowed_roles": ["Администратор", "Врач"]
        },
        "analysis_report": {
            "name": "Отчет по анализам",
            "fields": ["patient_name", "analysis_type", "results", "norm_values", "date", "lab_technician"],
            "allowed_roles": ["Администратор", "Врач", "Медсестра"]
        }
    }

class DocumentManager:
    def __init__(self):
        self.documents = []
    
    def create_document(self, template_id, data):
        """Создание нового документа по шаблону"""
        if template_id not in DocumentTemplate.TEMPLATES:
            raise ValueError("Неверный тип документа")
            
        template = DocumentTemplate.TEMPLATES[template_id]
        document = {
            "type": template_id,
            "name": template["name"],
            "data": data,
            "created_at": QDate.currentDate().toString("yyyy-MM-dd"),
            "status": "draft"
        }
        self.documents.append(document)
        return document

class DocumentDialog(QDialog):
    def __init__(self, template_id, patient_data=None, parent=None):
        super().__init__(parent)
        self.template_id = template_id
        self.patient_data = patient_data
        self.template = DocumentTemplate.TEMPLATES[template_id]
        
        self.setWindowTitle(f"Создание документа - {self.template['name']}")
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        self.fields = {}
        for field in self.template["fields"]:
            if field == "patient_name" and self.patient_data:
                field_input = QLineEdit(self.patient_data["name"])
            elif field == "date":
                field_input = QDateEdit()
                field_input.setDate(QDate.currentDate())
            else:
                field_input = QLineEdit()
            
            # Преобразуем имена полей для отображения
            field_label = field.replace("_", " ").title()
            layout.addRow(f"{field_label}:", field_input)
            self.fields[field] = field_input
        
        # Кнопки
        button_layout = QHBoxLayout()
        save_button = QPushButton("Создать документ")
        cancel_button = QPushButton("Отмена")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)
    
    def get_document_data(self):
        data = {}
        for field, widget in self.fields.items():
            if isinstance(widget, QDateEdit):
                data[field] = widget.date().toString("yyyy-MM-dd")
            else:
                data[field] = widget.text()
        return data

class UserManager:
    """Класс для управления пользователями"""
    def __init__(self):
        self.current_user = None
        self.users = USERS

    def login(self, username, password):
        """Аутентификация пользователя"""
        user = next((u for u in self.users if u["username"] == username and u["password"] == password), None)
        if user:
            user["last_login"] = QDate.currentDate().toString("yyyy-MM-dd")
            self.current_user = user
            return True
        return False

    def has_permission(self, permission):
        """Проверка прав доступа"""
        if not self.current_user:
            return False
        return permission in ROLE_PERMISSIONS.get(self.current_user["role"], [])

    def add_user(self, user_data):
        """Добавление нового пользователя"""
        if not self.has_permission("manage_users"):
            raise PermissionError("Недостаточно прав для управления пользователями")
        
        if any(u["username"] == user_data["username"] for u in self.users):
            raise ValueError("Пользователь с таким логином уже существует")
        
        self.users.append(user_data)

    def edit_user(self, username, new_data):
        """Редактирование пользователя"""
        if not self.has_permission("manage_users"):
            raise PermissionError("Недостаточно прав для управления пользователями")
        
        user_index = next((i for i, u in enumerate(self.users) if u["username"] == username), -1)
        if user_index == -1:
            raise ValueError("Пользователь не найден")
        
        # Нельзя редактировать логин администратора
        if self.users[user_index]["role"] == "Администратор" and new_data["role"] != "Администратор":
            raise ValueError("Нельзя изменить роль администратора")
        
        # Обновляем данные, сохраняя username
        original_username = self.users[user_index]["username"]
        self.users[user_index].update(new_data)
        self.users[user_index]["username"] = original_username
        
        return self.users[user_index]

    def delete_user(self, username):
        """Удаление пользователя"""
        if not self.has_permission("manage_users"):
            raise PermissionError("Недостаточно прав для управления пользователями")
        
        user_index = next((i for i, u in enumerate(self.users) if u["username"] == username), -1)
        if user_index == -1:
            raise ValueError("Пользователь не найден")
        
        # Нельзя удалить администратора или текущего пользователя
        if self.users[user_index]["role"] == "Администратор":
            raise ValueError("Нельзя удалить администратора")
        
        if self.users[user_index]["username"] == self.current_user["username"]:
            raise ValueError("Нельзя удалить свой аккаунт")
        
        del self.users[user_index]

    def get_all_users(self):
        """Получение списка всех пользователей"""
        if not self.has_permission("manage_users"):
            raise PermissionError("Недостаточно прав для просмотра пользователей")
        return self.users

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление пользователя")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(15)

        # Поля ввода
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.full_name_edit = QLineEdit()
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Врач", "Медсестра"])

        # Добавляем поля в форму
        layout.addRow("Логин:", self.username_edit)
        layout.addRow("Пароль:", self.password_edit)
        layout.addRow("ФИО:", self.full_name_edit)
        layout.addRow("Роль:", self.role_combo)

        # Кнопки
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)

    def get_user_data(self):
        return {
            "username": self.username_edit.text(),
            "password": self.password_edit.text(),
            "full_name": self.full_name_edit.text(),
            "role": self.role_combo.currentText(),
            "last_login": "",
            "status": "Активен"
        }

class EditUserDialog(QDialog):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setWindowTitle("Редактирование пользователя")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(15)

        # Поля для редактирования
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Оставьте пустым, чтобы не менять")
        
        self.full_name_edit = QLineEdit(self.user_data["full_name"])
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Врач", "Медсестра"])
        # Если пользователь администратор, блокируем возможность изменения роли
        if self.user_data["role"] == "Администратор":
            self.role_combo.addItem("Администратор")
            self.role_combo.setCurrentText("Администратор")
            self.role_combo.setEnabled(False)
        else:
            self.role_combo.setCurrentText(self.user_data["role"])
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Активен", "Заблокирован"])
        self.status_combo.setCurrentText(self.user_data["status"])

        # Добавляем поля в форму
        layout.addRow("Логин:", QLabel(self.user_data["username"]))
        layout.addRow("Новый пароль:", self.password_edit)
        layout.addRow("ФИО:", self.full_name_edit)
        layout.addRow("Роль:", self.role_combo)
        layout.addRow("Статус:", self.status_combo)

        # Кнопки
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)

    def get_user_data(self):
        data = {
            "full_name": self.full_name_edit.text(),
            "role": self.role_combo.currentText(),
            "status": self.status_combo.currentText()
        }
        
        # Добавляем пароль только если он был введён
        if self.password_edit.text():
            data["password"] = self.password_edit.text()
            
        return data

class AdminPanel(QDialog):
    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.setWindowTitle("Панель администратора")
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        header = QLabel("Панель администратора")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Вкладки
        tabs = QTabWidget()
        
        # Вкладка пользователей
        users_tab = QWidget()
        users_layout = QVBoxLayout(users_tab)
        
        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["Логин", "ФИО", "Роль", "Статус", "Последний вход", "Действия"])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        users_layout.addWidget(self.users_table)
        
        # Кнопки управления пользователями
        user_buttons = QHBoxLayout()
        add_user_btn = QPushButton("Добавить пользователя")
        add_user_btn.clicked.connect(self.add_user)
        user_buttons.addWidget(add_user_btn)
        user_buttons.addStretch()
        users_layout.addLayout(user_buttons)
        
        # Вкладка отчетов
        reports_tab = QWidget()
        reports_layout = QVBoxLayout(reports_tab)
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(4)
        self.reports_table.setHorizontalHeaderLabels(["Название", "Автор", "Дата создания", "Статус"])
        reports_layout.addWidget(self.reports_table)
        
        # Добавляем вкладки
        tabs.addTab(users_tab, "Пользователи")
        tabs.addTab(reports_tab, "Отчеты")
        
        layout.addWidget(tabs)
        
        # Загружаем данные пользователей
        self.load_users()

    def load_users(self):
        """Загрузка списка пользователей"""
        try:
            users = self.user_manager.get_all_users()
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                self.users_table.setItem(row, 0, QTableWidgetItem(user["username"]))
                self.users_table.setItem(row, 1, QTableWidgetItem(user["full_name"]))
                self.users_table.setItem(row, 2, QTableWidgetItem(user["role"]))
                self.users_table.setItem(row, 3, QTableWidgetItem(user["status"]))
                self.users_table.setItem(row, 4, QTableWidgetItem(user["last_login"]))
                
                # Кнопки действий
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("Изменить")
                edit_btn.clicked.connect(lambda checked, u=user["username"]: self.edit_user(u))
                
                delete_btn = QPushButton("Удалить")
                delete_btn.setStyleSheet("background-color: #e74c3c;")
                delete_btn.clicked.connect(lambda checked, u=user["username"]: self.delete_user(u))
                
                # Блокируем возможность удаления администратора
                if user["role"] == "Администратор":
                    delete_btn.setEnabled(False)
                    delete_btn.setToolTip("Нельзя удалить администратора")
                
                # Блокируем возможность удаления текущего пользователя
                if user["username"] == self.user_manager.current_user["username"] and user["role"] != "Администратор":
                    delete_btn.setEnabled(False)
                    delete_btn.setToolTip("Нельзя удалить текущего пользователя")
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                self.users_table.setCellWidget(row, 5, actions_widget)
            
            self.users_table.resizeColumnsToContents()
            
        except PermissionError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def add_user(self):
        """Добавление нового пользователя"""
        dialog = AddUserDialog(self)
        if dialog.exec():
            try:
                user_data = dialog.get_user_data()
                self.user_manager.add_user(user_data)
                self.load_users()
                QMessageBox.information(self, "Успех", "Пользователь успешно добавлен")
            except (PermissionError, ValueError) as e:
                QMessageBox.warning(self, "Ошибка", str(e))
    
    def edit_user(self, username):
        """Редактирование пользователя"""
        user = next((u for u in self.user_manager.users if u["username"] == username), None)
        if not user:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден")
            return
        
        dialog = EditUserDialog(user, self)
        if dialog.exec():
            try:
                new_data = dialog.get_user_data()
                self.user_manager.edit_user(username, new_data)
                self.load_users()
                QMessageBox.information(self, "Успех", "Пользователь успешно изменен")
            except (PermissionError, ValueError) as e:
                QMessageBox.warning(self, "Ошибка", str(e))
    
    def delete_user(self, username):
        """Удаление пользователя"""
        reply = QMessageBox.question(
            self, 
            "Подтверждение удаления", 
            f"Вы действительно хотите удалить пользователя {username}?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.user_manager.delete_user(username)
                self.load_users()
                QMessageBox.information(self, "Успех", "Пользователь успешно удален")
            except (PermissionError, ValueError) as e:
                QMessageBox.warning(self, "Ошибка", str(e))

class MainWindow(QMainWindow):
    def __init__(self, user_manager, on_logout):
        super().__init__()
        self.user_manager = user_manager
        self.on_logout = on_logout
        self.document_manager = DocumentManager()
        self.setWindowTitle("Медицинский центр - Список пациентов")
        self.setMinimumSize(1200, 700)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной макет
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Верхняя панель
        top_panel = QHBoxLayout()
        
        # Заголовок
        header_label = QLabel("Система управления пациентами")
        header_label.setStyleSheet("font-size: 28px; font-weight: bold; color: black;")
        top_panel.addWidget(header_label)
        
        # Кнопка выхода
        logout_button = QPushButton("Выйти")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                max-width: 100px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_button.clicked.connect(self.logout)
        top_panel.addWidget(logout_button)
        top_panel.setAlignment(logout_button, Qt.AlignRight)
        
        # Статистика
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_patients_label = QLabel("Всего пациентов: 0")
        self.active_patients_label = QLabel("На лечении: 0")
        self.discharged_patients_label = QLabel("Выписано: 0")
        
        for label in [self.total_patients_label, self.active_patients_label, self.discharged_patients_label]:
            label.setObjectName("statsLabel")
            stats_layout.addWidget(label)
        
        layout.addLayout(top_panel)
        layout.addLayout(stats_layout)
        
        # Таблица пациентов
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Возраст", "Диагноз", "Дата", "Статус"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        # Левая группа кнопок
        left_buttons = QHBoxLayout()
        add_button = QPushButton("Добавить пациента")
        add_button.clicked.connect(self.add_patient)
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete_patient)
        delete_button.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
        """)
        left_buttons.addWidget(add_button)
        left_buttons.addWidget(delete_button)
        
        # Правая группа кнопок
        right_buttons = QHBoxLayout()
        create_doc_button = QPushButton("Создать документ")
        create_doc_button.clicked.connect(self.show_document_menu)
        admin_button = QPushButton("Админ панель")
        admin_button.clicked.connect(self.show_admin_panel)
        
        right_buttons.addWidget(create_doc_button)
        right_buttons.addWidget(admin_button)
        
        buttons_layout.addLayout(left_buttons)
        buttons_layout.addStretch()
        buttons_layout.addLayout(right_buttons)
        layout.addLayout(buttons_layout)

        # Загружаем данные и обновляем статистику
        self.load_patients()
        self.update_statistics()

        # Добавляем тестовые данные пациентов
        self.add_test_patients()

    def load_patients(self):
        """Загрузка данных пациентов в таблицу"""
        self.table.setRowCount(len(SAMPLE_PATIENTS))
        for row, patient in enumerate(SAMPLE_PATIENTS):
            self.table.setItem(row, 0, QTableWidgetItem(str(patient["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(patient["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(patient["age"])))
            self.table.setItem(row, 3, QTableWidgetItem(patient["diagnosis"]))
            self.table.setItem(row, 4, QTableWidgetItem(patient["date"]))
            status_item = QTableWidgetItem(patient["status"])
            status_item.setTextAlignment(Qt.AlignCenter)
            if patient["status"] == "На лечении":
                status_item.setBackground(QColor("#f1c40f"))
            else:
                status_item.setBackground(QColor("#2ecc71"))
            self.table.setItem(row, 5, status_item)
        
        # Растягиваем колонки по содержимому
        self.table.resizeColumnsToContents()

    def update_statistics(self):
        """Обновление статистики"""
        total = len(SAMPLE_PATIENTS)
        active = sum(1 for p in SAMPLE_PATIENTS if p["status"] == "На лечении")
        discharged = total - active
        
        self.total_patients_label.setText(f"Всего пациентов: {total}")
        self.active_patients_label.setText(f"На лечении: {active}")
        self.discharged_patients_label.setText(f"Выписано: {discharged}")

    def add_patient(self):
        """Добавление нового пациента"""
        dialog = AddPatientDialog(self)
        if dialog.exec():
            patient_data = dialog.get_patient_data()
            patient_data["id"] = len(SAMPLE_PATIENTS) + 1
            SAMPLE_PATIENTS.append(patient_data)
            self.load_patients()
            self.update_statistics()

    def delete_patient(self):
        """Удаление выбранного пациента"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            patient_id = int(self.table.item(current_row, 0).text())
            reply = QMessageBox.question(self, "Подтверждение", 
                                       "Вы уверены, что хотите удалить этого пациента?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                SAMPLE_PATIENTS.pop(current_row)
                self.load_patients()
                self.update_statistics()

    def logout(self):
        """Обработка выхода из системы"""
        self.hide()
        self.on_logout()

    def show_document_menu(self):
        """Показать меню создания документов"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите пациента")
            return
        
        menu = QMenu(self)
        menu.addAction("Создать документ").triggered.connect(self.create_document)
        menu.addAction("Сгенерировать отчет").triggered.connect(self.show_report_dialog)
        
        menu.exec(QCursor.pos())
    
    def create_document(self):
        """Создание нового документа"""
        current_row = self.table.currentRow()
        if current_row < 0:
            return
            
        patient_data = {
            "name": self.table.item(current_row, 1).text(),
            "diagnosis": self.table.item(current_row, 3).text()
        }
        
        # Получаем доступные шаблоны для текущей роли
        current_role = self.user_manager.current_user["role"]
        available_templates = {
            t_id: t for t_id, t in DocumentTemplate.TEMPLATES.items()
            if current_role in t["allowed_roles"]
        }
        
        if not available_templates:
            QMessageBox.warning(
                self,
                "Ошибка",
                "У вас нет доступа к созданию документов"
            )
            return
        
        # Показываем диалог выбора типа документа
        selected_type, ok = QInputDialog.getItem(
            self,
            "Выбор типа документа",
            "Выберите тип документа:",
            [t["name"] for t in available_templates.values()],
            0,
            False
        )
        
        if ok and selected_type:
            # Находим ID шаблона по названию
            template_id = next(
                t_id for t_id, t in available_templates.items() 
                if t["name"] == selected_type
            )
            
            # Открываем диалог создания документа
            dialog = DocumentDialog(template_id, patient_data, self)
            if dialog.exec():
                document_data = dialog.get_document_data()
                document_data["created_by"] = self.user_manager.current_user["username"]
                document_data["created_by_role"] = current_role
                
                try:
                    document = self.document_manager.create_document(template_id, document_data)
                    QMessageBox.information(
                        self,
                        "Успех",
                        f"Документ '{document['name']}' успешно создан"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Ошибка",
                        f"Не удалось создать документ: {str(e)}"
                    )
    
    def show_report_dialog(self):
        """Показать диалог генерации отчета"""
        dialog = ReportDialog(self)
        dialog.exec()

    def show_admin_panel(self):
        """Показать панель администратора"""
        if self.user_manager.has_permission("manage_users"):
            admin_panel = AdminPanel(self.user_manager, self)
            admin_panel.exec()
        else:
            QMessageBox.warning(self, "Ошибка", "Недостаточно прав для доступа к панели администратора")

    def add_test_patients(self):
        """Добавление тестовых данных пациентов"""
        # Получаем текущую дату и соседние даты для тестовых данных
        current_date = QDate.currentDate().toString("yyyy-MM-dd")
        yesterday = QDate.currentDate().addDays(-1).toString("yyyy-MM-dd")
        week_ago = QDate.currentDate().addDays(-7).toString("yyyy-MM-dd")
        
        # Проверяем, нет ли уже пациентов в таблице
        if self.table.rowCount() > 0:
            return
            
        test_patients = [
            {"id": 1, "name": "Иванов Иван Иванович", "age": 45, "diagnosis": "Гипертония", "date": current_date, "status": "На лечении"},
            {"id": 2, "name": "Петрова Анна Сергеевна", "age": 32, "diagnosis": "ОРВИ", "date": current_date, "status": "Выписан"},
            {"id": 3, "name": "Сидоров Петр Николаевич", "age": 58, "diagnosis": "Артрит", "date": yesterday, "status": "На лечении"},
            {"id": 4, "name": "Кузнецова Елена Владимировна", "age": 27, "diagnosis": "Аллергия", "date": yesterday, "status": "Выписан"},
            {"id": 5, "name": "Смирнов Алексей Петрович", "age": 65, "diagnosis": "Диабет 2 типа", "date": week_ago, "status": "На лечении"},
            {"id": 6, "name": "Морозова Ольга Дмитриевна", "age": 19, "diagnosis": "Бронхит", "date": week_ago, "status": "На лечении"},
            {"id": 7, "name": "Волков Сергей Александрович", "age": 42, "diagnosis": "Гастрит", "date": current_date, "status": "На лечении"},
            {"id": 8, "name": "Лебедева Ирина Михайловна", "age": 71, "diagnosis": "Остеопороз", "date": yesterday, "status": "Выписан"},
            {"id": 9, "name": "Козлов Дмитрий Сергеевич", "age": 12, "diagnosis": "Ангина", "date": current_date, "status": "На лечении"},
            {"id": 10, "name": "Новикова Светлана Андреевна", "age": 54, "diagnosis": "Гипотиреоз", "date": week_ago, "status": "Выписан"}
        ]
        
        self.table.setRowCount(len(test_patients))
        for row, patient in enumerate(test_patients):
            self.table.setItem(row, 0, QTableWidgetItem(str(patient["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(patient["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(patient["age"])))
            self.table.setItem(row, 3, QTableWidgetItem(patient["diagnosis"]))
            self.table.setItem(row, 4, QTableWidgetItem(patient["date"]))
            
            # Создаем объект элемента статуса с правильным форматированием
            status_item = QTableWidgetItem(patient["status"])
            status_item.setTextAlignment(Qt.AlignCenter)
            if patient["status"] == "На лечении":
                status_item.setBackground(QColor("#f1c40f"))  # Желтый цвет для активных
            else:
                status_item.setBackground(QColor("#2ecc71"))  # Зеленый цвет для выписанных
            
            self.table.setItem(row, 5, status_item)
            
        # Обновляем статистику после добавления пациентов
        self.update_statistics()

class LoginWindow(QWidget):
    def __init__(self, user_manager, on_login):
        super().__init__()
        self.user_manager = user_manager
        self.on_login = on_login
        
        self.setWindowTitle("Авторизация - Медицинский центр")
        self.setFixedSize(450, 350)
        
        # Основной макет
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        # Заголовок
        header_label = QLabel("Медицинский центр")
        header_label.setStyleSheet("font-size: 28px; font-weight: bold; color: black;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Форма входа
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Введите логин")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("Логин:", self.username_edit)
        form_layout.addRow("Пароль:", self.password_edit)
        layout.addLayout(form_layout)
        
        # Кнопка входа
        login_button = QPushButton("Войти в систему")
        login_button.setFixedSize(200, 45)
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button, alignment=Qt.AlignCenter)

    def login(self):
        """Обработка входа в систему"""
        username = self.username_edit.text()
        password = self.password_edit.text()
        
        if username and password:
            if self.user_manager.login(username, password):
                self.hide()
                self.on_login()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите логин и пароль")

class ReportGenerator:
    """Класс для генерации отчетов в разных форматах"""
    
    @staticmethod
    def generate_excel_report(data, report_type, user_info):
        try:
            output = io.BytesIO()
            workbook = xlwt.Workbook()
            sheet = workbook.add_sheet(report_type[:31])  # Ограничение длины имени листа для Excel
            
            # Стили
            header_style = xlwt.easyxf('font: bold on; align: wrap on, vert centre, horiz center')
            date_style = xlwt.easyxf('font: bold off; align: wrap on, vert centre, horiz left')
            
            # Информация о создателе отчета
            sheet.write(0, 0, "Создан:", header_style)
            sheet.write(0, 1, f"{user_info['generated_by']} ({user_info['role']})")
            sheet.write(1, 0, "Дата:", header_style)
            sheet.write(1, 1, user_info['date'])
            
            if report_type == "Общий список пациентов":
                # Заголовки
                headers = ["ID", "ФИО", "Возраст", "Диагноз", "Дата", "Статус"]
                for col, header in enumerate(headers):
                    sheet.write(3, col, header, header_style)
                
                # Данные
                for row_idx, row in enumerate(data, 4):
                    sheet.write(row_idx, 0, row["id"])
                    sheet.write(row_idx, 1, row["name"])
                    sheet.write(row_idx, 2, row["age"])
                    sheet.write(row_idx, 3, row["diagnosis"])
                    sheet.write(row_idx, 4, row["date"])
                    sheet.write(row_idx, 5, row["status"])
                    
            elif report_type == "Статистика по диагнозам":
                # Подсчет статистики
                diagnosis_stats = {}
                for row in data:
                    diagnosis = row["diagnosis"]
                    diagnosis_stats[diagnosis] = diagnosis_stats.get(diagnosis, 0) + 1
                
                # Заголовки
                sheet.write(3, 0, "Диагноз", header_style)
                sheet.write(3, 1, "Количество пациентов", header_style)
                
                # Данные
                for row_idx, (diagnosis, count) in enumerate(diagnosis_stats.items(), 4):
                    sheet.write(row_idx, 0, diagnosis)
                    sheet.write(row_idx, 1, count)
                    
            else:  # Статистика по возрастным группам
                age_groups = {
                    "0-18": 0, "19-30": 0, "31-45": 0,
                    "46-60": 0, "60+": 0
                }
                
                for row in data:
                    try:
                        age = int(row["age"])
                        if age <= 18:
                            age_groups["0-18"] += 1
                        elif age <= 30:
                            age_groups["19-30"] += 1
                        elif age <= 45:
                            age_groups["31-45"] += 1
                        elif age <= 60:
                            age_groups["46-60"] += 1
                        else:
                            age_groups["60+"] += 1
                    except (ValueError, TypeError):
                        continue  # Пропускаем некорректные значения возраста
                
                # Заголовки
                sheet.write(3, 0, "Возрастная группа", header_style)
                sheet.write(3, 1, "Количество пациентов", header_style)
                
                # Данные
                for row_idx, (group, count) in enumerate(age_groups.items(), 4):
                    sheet.write(row_idx, 0, group)
                    sheet.write(row_idx, 1, count)
            
            workbook.save(output)
            return output.getvalue()
        except Exception as e:
            import traceback
            print(f"Ошибка при создании Excel: {str(e)}")
            print(traceback.format_exc())
            raise
    
    @staticmethod
    def generate_csv_report(data, report_type, user_info):
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Информация о создателе отчета
            writer.writerow(["Создан:", f"{user_info['generated_by']} ({user_info['role']})"])
            writer.writerow(["Дата:", user_info['date']])
            writer.writerow([])  # Пустая строка
            
            if report_type == "Общий список пациентов":
                # Заголовки
                writer.writerow(["ID", "ФИО", "Возраст", "Диагноз", "Дата", "Статус"])
                
                # Данные
                for row in data:
                    writer.writerow([
                        row["id"], row["name"], row["age"],
                        row["diagnosis"], row["date"], row["status"]
                    ])
                    
            elif report_type == "Статистика по диагнозам":
                diagnosis_stats = {}
                for row in data:
                    diagnosis = row["diagnosis"]
                    diagnosis_stats[diagnosis] = diagnosis_stats.get(diagnosis, 0) + 1
                
                writer.writerow(["Диагноз", "Количество пациентов"])
                for diagnosis, count in diagnosis_stats.items():
                    writer.writerow([diagnosis, count])
                    
            else:  # Статистика по возрастным группам
                age_groups = {
                    "0-18": 0, "19-30": 0, "31-45": 0,
                    "46-60": 0, "60+": 0
                }
                
                for row in data:
                    try:
                        age = int(row["age"])
                        if age <= 18:
                            age_groups["0-18"] += 1
                        elif age <= 30:
                            age_groups["19-30"] += 1
                        elif age <= 45:
                            age_groups["31-45"] += 1
                        elif age <= 60:
                            age_groups["46-60"] += 1
                        else:
                            age_groups["60+"] += 1
                    except (ValueError, TypeError):
                        continue  # Пропускаем некорректные значения возраста
                
                writer.writerow(["Возрастная группа", "Количество пациентов"])
                for group, count in age_groups.items():
                    writer.writerow([group, count])
            
            return output.getvalue()
        except Exception as e:
            import traceback
            print(f"Ошибка при создании CSV: {str(e)}")
            print(traceback.format_exc())
            raise

class ReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Генерация отчета")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        header = QLabel("Выберите тип и формат отчета")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)

        # Выбор типа отчета
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Общий список пациентов",
            "Статистика по диагнозам",
            "Статистика по возрастным группам"
        ])
        layout.addWidget(QLabel("Тип отчета:"))
        layout.addWidget(self.report_type_combo)
        
        # Период отчета
        date_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        # Устанавливаем начальную дату на месяц назад от текущей
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        
        date_layout.addWidget(QLabel("С:"))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("По:"))
        date_layout.addWidget(self.end_date)
        layout.addLayout(date_layout)
        
        # Кнопки для разных форматов
        layout.addWidget(QLabel("\nФормат отчета:"))
        
        excel_btn = QPushButton("Скачать Excel")
        excel_btn.clicked.connect(lambda: self.generate_report("excel"))
        
        csv_btn = QPushButton("Скачать CSV")
        csv_btn.clicked.connect(lambda: self.generate_report("csv"))
        
        layout.addWidget(excel_btn)
        layout.addWidget(csv_btn)
    
    def generate_report(self, format_type):
        if not self.parent.user_manager.has_permission("create_report"):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для создания отчетов")
            return

        report_type = self.report_type_combo.currentText()
        start_date = self.start_date.date()
        end_date = self.end_date.date()

        # Получаем все данные из таблицы независимо от фильтров
        data = []
        for row in range(self.parent.table.rowCount()):
            try:
                patient_id = self.parent.table.item(row, 0).text()
                name = self.parent.table.item(row, 1).text()
                age = self.parent.table.item(row, 2).text()
                diagnosis = self.parent.table.item(row, 3).text()
                date_str = self.parent.table.item(row, 4).text()
                status = self.parent.table.item(row, 5).text()
                
                data.append({
                    "id": patient_id,
                    "name": name,
                    "age": age,
                    "diagnosis": diagnosis,
                    "date": date_str,
                    "status": status
                })
            except Exception as e:
                print(f"Ошибка при обработке строки {row}: {str(e)}")
                continue
        
        try:
            # Проверяем, есть ли данные для отчета
            if not data:
                QMessageBox.warning(self, "Предупреждение", "Нет данных для создания отчета")
                return
                
            # Добавляем информацию о пользователе в отчет
            user_info = {
                "generated_by": self.parent.user_manager.current_user["full_name"],
                "role": self.parent.user_manager.current_user["role"],
                "date": QDate.currentDate().toString("yyyy-MM-dd")
            }

            if format_type == "excel":
                content = ReportGenerator.generate_excel_report(data, report_type, user_info)
                file_ext = "xls"
            else:  # csv
                content = ReportGenerator.generate_csv_report(data, report_type, user_info)
                file_ext = "csv"
            
            # Сохранение файла
            sanitized_report_type = ''.join(c for c in report_type if c.isalnum() or c in [' ', '-', '_']).replace(' ', '_')
            filename = f"medical_report_{sanitized_report_type}_{QDate.currentDate().toString('yyyy-MM-dd')}.{file_ext}"
            
            with open(filename, 'wb') as f:
                if isinstance(content, str):
                    f.write(content.encode('utf-8'))
                else:
                    f.write(content)
            
            QMessageBox.information(self, "Успех", f"Отчет сохранен как {filename}")
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать отчет: {str(e)}")

class MedicalCenterApp:
    def __init__(self):
        # Создание приложения
        self.app = QApplication(sys.argv)
        
        # Применяем глобальные стили
        self.app.setStyle("Fusion")
        self.app.setStyleSheet(StyleHelper.get_main_style())
        
        # Создаем менеджер пользователей
        self.user_manager = UserManager()
        
        # Создаем окна
        self.login_window = LoginWindow(self.user_manager, self.show_main_window)
        self.main_window = None
    
    def show_main_window(self):
        """Показать главное окно после успешного входа"""
        self.login_window.hide()
        if not self.main_window:
            self.main_window = MainWindow(self.user_manager, self.show_login_window)
        self.main_window.show()
    
    def show_login_window(self):
        """Показать окно входа"""
        if self.main_window:
            self.main_window.hide()
        self.login_window.show()
        # Очищаем поля логина
        self.login_window.username_edit.clear()
        self.login_window.password_edit.clear()
    
    def run(self):
        """Запуск приложения"""
        self.login_window.show()
        return self.app.exec()

if __name__ == '__main__':
    app = MedicalCenterApp()
    app.run() 