from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QComboBox, QPushButton,
                               QVBoxLayout, QHBoxLayout, QMessageBox, QFormLayout, 
                               QTableWidget, QTableWidgetItem, QLineEdit, QDialog,
                               QTabWidget, QGroupBox, QScrollArea, QFrame, QListWidget,
                               QListWidgetItem, QGridLayout, QDateEdit, QSpinBox,
                               QRadioButton, QButtonGroup, QCheckBox, QTextEdit,
                               QHeaderView, QStackedWidget, QSplitter)
from PySide6.QtCore import Qt, Signal, QDate, QSize, QTimer
from PySide6.QtGui import QFont, QIcon, QColor, QPixmap
from datetime import datetime, timedelta
import sys
import json
import os

from database_connection import db

class AddEditUserDialog(QDialog):
    """Диалог добавления/редактирования пользователя"""
    
    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data  # None, если создаем нового пользователя
        
        self.setWindowTitle("Добавление пользователя" if user_data is None else "Редактирование пользователя")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса диалога"""
        layout = QVBoxLayout()
        
        # Форма с полями ввода
        form_layout = QFormLayout()
        
        # Имя пользователя
        self.username_input = QLineEdit()
        if self.user_data:
            self.username_input.setText(self.user_data.get('username', ''))
            # Запрещаем изменение логина только для администратора
            if self.user_data.get('username') == 'admin':
                self.username_input.setEnabled(False)  # Запрещаем изменение логина администратора
        form_layout.addRow("Логин:", self.username_input)
        
        # Пароль
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Пароль:", self.password_input)
        
        # ФИО
        self.full_name_input = QLineEdit()
        if self.user_data:
            self.full_name_input.setText(self.user_data.get('full_name', ''))
        form_layout.addRow("ФИО:", self.full_name_input)
        
        # Email
        self.email_input = QLineEdit()
        if self.user_data:
            self.email_input.setText(self.user_data.get('email', ''))
        form_layout.addRow("Email:", self.email_input)
        
        # Роль
        self.role_combo = QComboBox()
        self.role_combo.addItem("Администратор", "admin")
        self.role_combo.addItem("Врач", "doctor")
        self.role_combo.addItem("Лаборант", "lab")
        
        if self.user_data:
            role = self.user_data.get('role', '')
            index = self.role_combo.findData(role)
            if index >= 0:
                self.role_combo.setCurrentIndex(index)
        
        form_layout.addRow("Роль:", self.role_combo)
        
        # Специализация (только для врачей)
        self.specialization_input = QLineEdit()
        self.specialization_input.setVisible(False)
        self.specialization_label = QLabel("Специализация:")
        self.specialization_label.setVisible(False)
        form_layout.addRow(self.specialization_label, self.specialization_input)
        
        # Статус (только для редактирования)
        if self.user_data:
            self.status_combo = QComboBox()
            self.status_combo.addItem("Активен", "active")
            self.status_combo.addItem("Заблокирован", "blocked")
            
            status = self.user_data.get('status', 'active')
            index = self.status_combo.findData(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
            
            form_layout.addRow("Статус:", self.status_combo)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_user)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Обработка изменения роли
        self.role_combo.currentIndexChanged.connect(self.on_role_changed)
        self.on_role_changed(self.role_combo.currentIndex())
    
    def on_role_changed(self, index):
        """Обработка изменения роли пользователя"""
        role = self.role_combo.itemData(index)
        
        # Показываем поле специализации только для врачей
        is_doctor = (role == "doctor")
        self.specialization_input.setVisible(is_doctor)
        self.specialization_label.setVisible(is_doctor)
        
        # Обновляем размер окна
        self.adjustSize()
    
    def save_user(self):
        """Сохранение данных пользователя"""
        # Валидация данных
        username = self.username_input.text().strip()
        password = self.password_input.text()
        full_name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        role = self.role_combo.currentData()
        
        if not username:
            QMessageBox.warning(self, "Ошибка", "Логин не может быть пустым")
            return
        
        if not self.user_data and not password:
            QMessageBox.warning(self, "Ошибка", "Пароль не может быть пустым")
            return
        
        if not full_name:
            QMessageBox.warning(self, "Ошибка", "ФИО не может быть пустым")
            return
        
        # Проверка уникальности логина для нового пользователя
        if not self.user_data:
            user_check = db.fetch_one("SELECT id FROM users WHERE username = ?", (username,))
            if user_check:
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")
                return
        # Проверка уникальности логина при редактировании (если логин был изменен)
        elif self.user_data and username != self.user_data['username']:
            user_check = db.fetch_one("SELECT id FROM users WHERE username = ?", (username,))
            if user_check:
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")
                return
        
        try:
            if self.user_data:  # Редактирование существующего пользователя
                user_id = self.user_data['id']
                status = self.status_combo.currentData()
                
                # Защита от смены роли для главного администратора (admin)
                if self.user_data['username'] == 'admin' and role != 'admin':
                    QMessageBox.warning(self, "Ошибка", "Нельзя изменить роль главного администратора")
                    return
                
                # Базовый запрос на обновление
                if self.user_data['username'] == 'admin':
                    # Для администратора обновляем только основные данные без роли
                    query = """
                    UPDATE users 
                    SET full_name = ?, email = ?, status = ?
                    """
                    params = [full_name, email, status]
                else:
                    # Для всех остальных пользователей обновляем все данные включая роль
                    # Также обновляем логин, если он был изменен
                    if username != self.user_data['username']:
                        query = """
                        UPDATE users 
                        SET username = ?, full_name = ?, email = ?, role = ?, status = ?
                        """
                        params = [username, full_name, email, role, status]
                    else:
                        query = """
                        UPDATE users 
                        SET full_name = ?, email = ?, role = ?, status = ?
                        """
                        params = [full_name, email, role, status]
                
                # Добавляем пароль, если он был введен
                if password:
                    query += ", password = ?"
                    params.append(password)
                
                query += " WHERE id = ?"
                params.append(user_id)
                
                print(f"Выполнение обновления пользователя: {query}")
                print(f"Параметры: {params}")
                
                if db.execute_query(query, params):
                    # Обновление информации о враче, если это врач
                    if role == "doctor":
                        specialization = self.specialization_input.text().strip()
                        
                        # Проверяем, существует ли уже запись о враче
                        doctor = db.fetch_one("SELECT id FROM doctors WHERE user_id = ?", (user_id,))
                        
                        if doctor:
                            db.execute_query(
                                "UPDATE doctors SET specialization = ? WHERE user_id = ?",
                                (specialization, user_id)
                            )
                        else:
                            db.execute_query(
                                "INSERT INTO doctors (user_id, specialization) VALUES (?, ?)",
                                (user_id, specialization)
                            )
                    
                    QMessageBox.information(self, "Успех", "Пользователь успешно обновлен")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить пользователя")
            else:  # Добавление нового пользователя
                # Добавление пользователя
                print(f"Добавление нового пользователя: {username}, {role}")
                user_id = db.add_user(username, password, full_name, role, email)
                
                if user_id:
                    # Добавление информации о враче, если это врач
                    if role == "doctor":
                        specialization = self.specialization_input.text().strip()
                        db.execute_query(
                            "INSERT INTO doctors (user_id, specialization) VALUES (?, ?)",
                            (user_id, specialization)
                        )
                    
                    QMessageBox.information(self, "Успех", "Пользователь успешно добавлен")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось добавить пользователя")
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")


class UserListWidget(QWidget):
    """Виджет для отображения списка пользователей"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        
        # Верхняя панель с кнопками
        top_panel = QHBoxLayout()
        
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.load_users)
        top_panel.addWidget(refresh_button)
        
        add_button = QPushButton("Добавить пользователя")
        add_button.clicked.connect(self.add_user)
        top_panel.addWidget(add_button)
        
        top_panel.addStretch()
        
        layout.addLayout(top_panel)
        
        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "Логин", "ФИО", "Роль", "Email", "Последний вход", "Действия"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.users_table)
        
        # Загрузка пользователей
        self.load_users()
    
    def load_users(self):
        """Загрузка списка пользователей"""
        users = db.get_all_users()
        
        self.users_table.setRowCount(len(users))
        
        # Маппинг ролей для отображения
        role_map = {
            'admin': 'Администратор',
            'doctor': 'Врач',
            'lab': 'Лаборант'
        }
        
        for row, user in enumerate(users):
            # Логин
            username_item = QTableWidgetItem(user.get('username', ''))
            username_item.setData(Qt.UserRole, user)  # Сохраняем все данные пользователя
            self.users_table.setItem(row, 0, username_item)
            
            # ФИО
            self.users_table.setItem(row, 1, QTableWidgetItem(user.get('full_name', '')))
            
            # Роль
            role_item = QTableWidgetItem(role_map.get(user.get('role', ''), user.get('role', '')))
            self.users_table.setItem(row, 2, role_item)
            
            # Email
            self.users_table.setItem(row, 3, QTableWidgetItem(user.get('email', '')))
            
            # Последний вход
            last_login = user.get('last_login', '')
            self.users_table.setItem(row, 4, QTableWidgetItem(last_login))
            
            # Ячейка с кнопками действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_button = QPushButton("Редактировать")
            edit_button.clicked.connect(lambda checked, u=user: self.edit_user(u))
            actions_layout.addWidget(edit_button)
            
            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda checked, u=user: self.delete_user(u))
            actions_layout.addWidget(delete_button)
            
            self.users_table.setCellWidget(row, 5, actions_widget)
    
    def add_user(self):
        """Добавление нового пользователя"""
        dialog = AddEditUserDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_users()  # Обновляем список пользователей
    
    def edit_user(self, user):
        """Редактирование существующего пользователя"""
        dialog = AddEditUserDialog(user, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_users()  # Обновляем список пользователей
    
    def delete_user(self, user):
        """Удаление пользователя"""
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить пользователя {user.get('username')}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Удаление врача, если это врач
                if user.get('role') == 'doctor':
                    db.execute_query("DELETE FROM doctors WHERE user_id = ?", (user.get('id'),))
                
                # Удаление пользователя
                result = db.execute_query("DELETE FROM users WHERE id = ?", (user.get('id'),))
                
                if result:
                    QMessageBox.information(self, "Успех", "Пользователь успешно удален")
                    self.load_users()  # Обновляем список пользователей
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить пользователя")
            
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при удалении: {str(e)}")


class SystemStatisticsWidget(QWidget):
    """Виджет для отображения статистики системы"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        
        # Верхняя панель с фильтрами
        top_panel = QHBoxLayout()
        
        period_label = QLabel("Период:")
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        
        to_label = QLabel("по")
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        
        apply_button = QPushButton("Применить")
        apply_button.clicked.connect(self.load_statistics)
        
        top_panel.addWidget(period_label)
        top_panel.addWidget(self.start_date)
        top_panel.addWidget(to_label)
        top_panel.addWidget(self.end_date)
        top_panel.addWidget(apply_button)
        top_panel.addStretch()
        
        layout.addLayout(top_panel)
        
        # Панель с блоками статистики
        self.statistics_area = QScrollArea()
        self.statistics_area.setWidgetResizable(True)
        
        statistics_widget = QWidget()
        self.statistics_layout = QVBoxLayout(statistics_widget)
        
        self.statistics_area.setWidget(statistics_widget)
        layout.addWidget(self.statistics_area)
        
        # Загрузка статистики
        self.load_statistics()
    
    def load_statistics(self):
        """Загрузка статистики"""
        # Очистка предыдущих данных
        for i in reversed(range(self.statistics_layout.count())):
            widget = self.statistics_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Получение параметров фильтрации
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Статистика пользователей
        self._add_user_statistics()
        
        # Статистика пациентов
        self._add_patient_statistics(start_date, end_date)
        
        # Статистика анализов
        self._add_analysis_statistics(start_date, end_date)
        
        # Статистика приемов
        self._add_appointment_statistics(start_date, end_date)
    
    def _add_user_statistics(self):
        """Добавление блока статистики пользователей"""
        group_box = QGroupBox("Статистика пользователей")
        layout = QVBoxLayout()
        
        # Общее количество пользователей
        users = db.fetch_all("SELECT role, COUNT(*) as count FROM users GROUP BY role")
        
        # Маппинг ролей для отображения
        role_map = {
            'admin': 'Администраторы',
            'doctor': 'Врачи',
            'lab': 'Лаборанты'
        }
        
        user_stats = QLabel("Пользователи в системе:")
        layout.addWidget(user_stats)
        
        for role_stat in users:
            role = role_stat.get('role', '')
            count = role_stat.get('count', 0)
            role_label = QLabel(f"• {role_map.get(role, role)}: {count}")
            layout.addWidget(role_label)
        
        group_box.setLayout(layout)
        self.statistics_layout.addWidget(group_box)
    
    def _add_patient_statistics(self, start_date, end_date):
        """Добавление блока статистики пациентов"""
        group_box = QGroupBox("Статистика пациентов")
        layout = QVBoxLayout()
        
        # Общее количество пациентов
        total_patients = db.fetch_one("SELECT COUNT(*) as count FROM patients")
        total_label = QLabel(f"Всего пациентов: {total_patients.get('count', 0)}")
        layout.addWidget(total_label)
        
        # Количество новых пациентов за период
        new_patients = db.fetch_one(
            "SELECT COUNT(*) as count FROM patients WHERE date(created_at) BETWEEN ? AND ?",
            (start_date, end_date)
        )
        new_patients_label = QLabel(f"Новых пациентов за период: {new_patients.get('count', 0)}")
        layout.addWidget(new_patients_label)
        
        group_box.setLayout(layout)
        self.statistics_layout.addWidget(group_box)
    
    def _add_analysis_statistics(self, start_date, end_date):
        """Добавление блока статистики анализов"""
        group_box = QGroupBox("Статистика анализов")
        layout = QVBoxLayout()
        
        # Общее количество анализов за период
        total_analyses = db.fetch_one(
            "SELECT COUNT(*) as count FROM analysis_results WHERE date(result_date) BETWEEN ? AND ?",
            (start_date, end_date)
        )
        total_label = QLabel(f"Всего анализов за период: {total_analyses.get('count', 0)}")
        layout.addWidget(total_label)
        
        # Количество анализов по типам
        analyses_by_type = db.fetch_all("""
            SELECT at.name, COUNT(ar.id) as count
            FROM analysis_results ar
            JOIN analysis_types at ON ar.analysis_type_id = at.id
            WHERE date(ar.result_date) BETWEEN ? AND ?
            GROUP BY at.name
            ORDER BY count DESC
        """, (start_date, end_date))
        
        if analyses_by_type:
            types_label = QLabel("Анализы по типам:")
            layout.addWidget(types_label)
            
            for type_stat in analyses_by_type:
                type_name = type_stat.get('name', '')
                count = type_stat.get('count', 0)
                type_label = QLabel(f"• {type_name}: {count}")
                layout.addWidget(type_label)
        else:
            no_data_label = QLabel("Нет данных о проведенных анализах за указанный период")
            layout.addWidget(no_data_label)
        
        group_box.setLayout(layout)
        self.statistics_layout.addWidget(group_box)
    
    def _add_appointment_statistics(self, start_date, end_date):
        """Добавление блока статистики приемов"""
        group_box = QGroupBox("Статистика приемов")
        layout = QVBoxLayout()
        
        # Общее количество приемов за период
        total_appointments = db.fetch_one(
            "SELECT COUNT(*) as count FROM appointments WHERE date(appointment_date) BETWEEN ? AND ?",
            (start_date, end_date)
        )
        total_label = QLabel(f"Всего приемов за период: {total_appointments.get('count', 0)}")
        layout.addWidget(total_label)
        
        # Количество приемов по статусам
        appointments_by_status = db.fetch_all("""
            SELECT status, COUNT(*) as count
            FROM appointments
            WHERE date(appointment_date) BETWEEN ? AND ?
            GROUP BY status
        """, (start_date, end_date))
        
        # Маппинг статусов для отображения
        status_map = {
            'scheduled': 'Запланировано',
            'completed': 'Завершено',
            'cancelled': 'Отменено'
        }
        
        if appointments_by_status:
            status_label = QLabel("Приемы по статусам:")
            layout.addWidget(status_label)
            
            for status_stat in appointments_by_status:
                status = status_stat.get('status', '')
                count = status_stat.get('count', 0)
                status_label = QLabel(f"• {status_map.get(status, status)}: {count}")
                layout.addWidget(status_label)
        else:
            no_data_label = QLabel("Нет данных о приемах за указанный период")
            layout.addWidget(no_data_label)
        
        group_box.setLayout(layout)
        self.statistics_layout.addWidget(group_box)


class PatientListWidget(QWidget):
    """Виджет для отображения списка пациентов"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        
        # Верхняя панель с кнопками и поиском
        top_panel = QHBoxLayout()
        
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.load_patients)
        top_panel.addWidget(refresh_button)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск пациента")
        self.search_input.textChanged.connect(self.filter_patients)
        top_panel.addWidget(self.search_input)
        
        top_panel.addStretch()
        
        layout.addLayout(top_panel)
        
        # Таблица пациентов
        self.patients_table = QTableWidget()
        self.patients_table.setColumnCount(6)
        self.patients_table.setHorizontalHeaderLabels([
            "ID", "ФИО", "Дата рождения", "Телефон", "Email", "Адрес"
        ])
        self.patients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.patients_table)
        
        # Загрузка пациентов
        self.load_patients()
    
    def load_patients(self):
        """Загрузка списка пациентов"""
        patients = db.get_all_patients()
        self.all_patients = patients  # Сохраняем для фильтрации
        
        self.update_table(patients)
    
    def update_table(self, patients):
        """Обновление таблицы пациентов"""
        self.patients_table.setRowCount(len(patients))
        
        for row, patient in enumerate(patients):
            # ID
            self.patients_table.setItem(row, 0, QTableWidgetItem(str(patient.get('id', ''))))
            
            # ФИО
            self.patients_table.setItem(row, 1, QTableWidgetItem(patient.get('full_name', '')))
            
            # Дата рождения
            self.patients_table.setItem(row, 2, QTableWidgetItem(patient.get('birth_date', '')))
            
            # Телефон
            self.patients_table.setItem(row, 3, QTableWidgetItem(patient.get('phone', '')))
            
            # Email
            self.patients_table.setItem(row, 4, QTableWidgetItem(patient.get('email', '')))
            
            # Адрес
            self.patients_table.setItem(row, 5, QTableWidgetItem(patient.get('address', '')))
    
    def filter_patients(self):
        """Фильтрация пациентов по поисковому запросу"""
        search_text = self.search_input.text().lower()
        
        if not search_text:
            # Если строка поиска пуста, показываем всех пациентов
            self.update_table(self.all_patients)
            return
        
        # Фильтрация пациентов
        filtered_patients = []
        for patient in self.all_patients:
            full_name = patient.get('full_name', '').lower()
            phone = patient.get('phone', '').lower()
            email = patient.get('email', '').lower()
            
            if (search_text in full_name or 
                search_text in phone or 
                search_text in email):
                filtered_patients.append(patient)
        
        self.update_table(filtered_patients)


class AdminWindow(QMainWindow):
    """Главное окно интерфейса администратора"""
    logout_signal = Signal()
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        
        self.setWindowTitle(f"Медицинский центр - Администратор: {user_data['full_name']}")
        self.setMinimumSize(900, 700)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        
        # Верхняя панель с информацией о пользователе и кнопками
        top_panel = QHBoxLayout()
        
        user_info = QLabel(f"Администратор: {self.user_data['full_name']}")
        user_info.setStyleSheet("font-weight: bold;")
        top_panel.addWidget(user_info)
        
        top_panel.addStretch()
        
        logout_button = QPushButton("Выйти")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        logout_button.clicked.connect(self.logout)
        top_panel.addWidget(logout_button)
        
        main_layout.addLayout(top_panel)
        
        # Добавление разделительной линии
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Создание вкладок
        self.tab_widget = QTabWidget()
        
        # Вкладка пользователей
        self.users_tab = UserListWidget()
        self.tab_widget.addTab(self.users_tab, "Пользователи")
        
        # Вкладка пациентов
        self.patients_tab = PatientListWidget()
        self.tab_widget.addTab(self.patients_tab, "Пациенты")
        
        # Вкладка статистики
        self.statistics_tab = SystemStatisticsWidget()
        self.tab_widget.addTab(self.statistics_tab, "Статистика")
        
        main_layout.addWidget(self.tab_widget)
    
    def logout(self):
        """Выход из системы"""
        reply = QMessageBox.question(
            self, 
            "Подтверждение выхода", 
            "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.logout_signal.emit()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Тестовое подключение к базе данных
    db.connect("1")  # Пароль для базы данных
    
    # Тестовый пользователь
    test_user = {
        'id': 1,
        'username': 'admin',
        'full_name': 'Администратор Системы',
        'role': 'admin'
    }
    
    window = AdminWindow(test_user)
    window.show()
    
    sys.exit(app.exec()) 