from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTabWidget, QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QDateEdit, QGroupBox, QFormLayout, QMessageBox,
                             QSplitter, QLineEdit, QDialog, QTimeEdit, QRadioButton,
                             QButtonGroup, QFileDialog)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont
import os
import datetime

from app.database.database import Database
from app.models.models import UserRole
from app.utils.document_generator import DocumentGenerator
from app.utils.email_sender import EmailSender

class AdminWindow(QMainWindow):
    """Окно интерфейса администратора"""
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.document_generator = DocumentGenerator()
        self.email_sender = EmailSender()
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        # Настройка окна
        self.setWindowTitle(f"Администратор - {self.user_data['full_name']}")
        self.setMinimumSize(1000, 700)
        
        # Основной виджет и макет
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Заголовок
        header_label = QLabel("Система управления медицинским центром")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        
        # Создаем вкладки
        self.create_analysis_tab()
        self.create_patients_tab()
        self.create_appointments_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Устанавливаем центральный виджет
        self.setCentralWidget(central_widget)
    
    def create_analysis_tab(self):
        """Создание вкладки для работы с анализами"""
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        
        # Фильтры для анализов
        analysis_filters_group = QGroupBox("Фильтры")
        analysis_filters_layout = QHBoxLayout()
        
        # Выбор пациента
        patient_label = QLabel("Пациент:")
        self.patient_combo = QComboBox()
        self.patient_combo.setMinimumWidth(200)
        self.refresh_patient_list()
        
        # Выбор типа анализа
        analysis_type_label = QLabel("Тип анализа:")
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.setMinimumWidth(200)
        self.refresh_analysis_types()
        
        # Выбор даты начала
        from_date_label = QLabel("С:")
        self.analysis_from_date = QDateEdit()
        self.analysis_from_date.setDate(QDate.currentDate().addDays(-30))
        self.analysis_from_date.setCalendarPopup(True)
        
        # Выбор даты окончания
        to_date_label = QLabel("По:")
        self.analysis_to_date = QDateEdit()
        self.analysis_to_date.setDate(QDate.currentDate())
        self.analysis_to_date.setCalendarPopup(True)
        
        # Кнопка применения фильтров
        apply_analysis_filters_button = QPushButton("Применить")
        apply_analysis_filters_button.clicked.connect(self.refresh_analysis_results)
        
        # Кнопка очистки фильтров
        clear_analysis_filters_button = QPushButton("Сбросить")
        clear_analysis_filters_button.clicked.connect(self.clear_analysis_filters)
        
        # Размещение фильтров
        analysis_filters_layout.addWidget(patient_label)
        analysis_filters_layout.addWidget(self.patient_combo)
        analysis_filters_layout.addWidget(analysis_type_label)
        analysis_filters_layout.addWidget(self.analysis_type_combo)
        analysis_filters_layout.addWidget(from_date_label)
        analysis_filters_layout.addWidget(self.analysis_from_date)
        analysis_filters_layout.addWidget(to_date_label)
        analysis_filters_layout.addWidget(self.analysis_to_date)
        analysis_filters_layout.addStretch()
        analysis_filters_layout.addWidget(apply_analysis_filters_button)
        analysis_filters_layout.addWidget(clear_analysis_filters_button)
        
        analysis_filters_group.setLayout(analysis_filters_layout)
        analysis_layout.addWidget(analysis_filters_group)
        
        # Таблица анализов
        self.analysis_table = QTableWidget()
        self.analysis_table.setColumnCount(7)
        self.analysis_table.setHorizontalHeaderLabels([
            "Дата", "Пациент", "Тип анализа", "Статус", "Лаборант", "Документы", "Email"
        ])
        self.analysis_table.horizontalHeader().setStretchLastSection(True)
        self.analysis_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        analysis_layout.addWidget(self.analysis_table)
        
        # Добавление вкладки
        self.tab_widget.addTab(analysis_tab, "Анализы")
    
    def create_patients_tab(self):
        """Создание вкладки для работы с пациентами"""
        patients_tab = QWidget()
        patients_layout = QVBoxLayout(patients_tab)
        
        # Таблица пациентов
        self.patients_table = QTableWidget()
        self.patients_table.setColumnCount(7)
        self.patients_table.setHorizontalHeaderLabels([
            "ФИО", "Дата рождения", "Пол", "Телефон", "Email", "Адрес", "Действия"
        ])
        self.patients_table.horizontalHeader().setStretchLastSection(True)
        self.patients_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        patients_layout.addWidget(self.patients_table)
        
        # Кнопки для работы с пациентами
        buttons_layout = QHBoxLayout()
        
        add_patient_button = QPushButton("Добавить пациента")
        add_patient_button.clicked.connect(self.add_patient_dialog)
        
        refresh_patients_button = QPushButton("Обновить")
        refresh_patients_button.clicked.connect(self.refresh_patients)
        
        buttons_layout.addWidget(add_patient_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(refresh_patients_button)
        
        patients_layout.addLayout(buttons_layout)
        
        # Добавление вкладки
        self.tab_widget.addTab(patients_tab, "Пациенты")
        
        # Загружаем пациентов
        self.refresh_patients()
    
    def create_appointments_tab(self):
        """Создание вкладки для работы с расписанием"""
        appointments_tab = QWidget()
        appointments_layout = QVBoxLayout(appointments_tab)
        
        # Фильтры для расписания
        appointments_filters_group = QGroupBox("Фильтры")
        appointments_filters_layout = QHBoxLayout()
        
        # Выбор врача
        doctor_label = QLabel("Врач:")
        self.doctor_combo = QComboBox()
        self.doctor_combo.setMinimumWidth(200)
        self.refresh_doctor_list()
        
        # Выбор пациента
        patient_label = QLabel("Пациент:")
        self.appointment_patient_combo = QComboBox()
        self.appointment_patient_combo.setMinimumWidth(200)
        # Копируем список пациентов из другой вкладки
        self.appointment_patient_combo.clear()
        self.appointment_patient_combo.addItem("Все пациенты", None)
        patients = self.db.get_all_patients()
        for patient in patients:
            self.appointment_patient_combo.addItem(f"{patient[1]} ({patient[2]})", patient[0])
        
        # Выбор даты начала
        from_date_label = QLabel("С:")
        self.appointment_from_date = QDateEdit()
        self.appointment_from_date.setDate(QDate.currentDate())
        self.appointment_from_date.setCalendarPopup(True)
        
        # Выбор даты окончания
        to_date_label = QLabel("По:")
        self.appointment_to_date = QDateEdit()
        self.appointment_to_date.setDate(QDate.currentDate().addDays(7))
        self.appointment_to_date.setCalendarPopup(True)
        
        # Кнопка применения фильтров
        apply_appointments_filters_button = QPushButton("Применить")
        apply_appointments_filters_button.clicked.connect(self.refresh_appointments)
        
        # Кнопка очистки фильтров
        clear_appointments_filters_button = QPushButton("Сбросить")
        clear_appointments_filters_button.clicked.connect(self.clear_appointments_filters)
        
        # Размещение фильтров
        appointments_filters_layout.addWidget(doctor_label)
        appointments_filters_layout.addWidget(self.doctor_combo)
        appointments_filters_layout.addWidget(patient_label)
        appointments_filters_layout.addWidget(self.appointment_patient_combo)
        appointments_filters_layout.addWidget(from_date_label)
        appointments_filters_layout.addWidget(self.appointment_from_date)
        appointments_filters_layout.addWidget(to_date_label)
        appointments_filters_layout.addWidget(self.appointment_to_date)
        appointments_filters_layout.addStretch()
        appointments_filters_layout.addWidget(apply_appointments_filters_button)
        appointments_filters_layout.addWidget(clear_appointments_filters_button)
        
        appointments_filters_group.setLayout(appointments_filters_layout)
        appointments_layout.addWidget(appointments_filters_group)
        
        # Таблица расписания
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(7)
        self.appointments_table.setHorizontalHeaderLabels([
            "Дата", "Время", "Пациент", "Врач", "Статус", "Примечания", "Действия"
        ])
        self.appointments_table.horizontalHeader().setStretchLastSection(True)
        self.appointments_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        appointments_layout.addWidget(self.appointments_table)
        
        # Кнопка добавления нового приема
        add_appointment_button = QPushButton("Добавить прием")
        add_appointment_button.clicked.connect(self.add_appointment_dialog)
        appointments_layout.addWidget(add_appointment_button)
        
        # Добавление вкладки
        self.tab_widget.addTab(appointments_tab, "Расписание")
        
        # Загружаем расписание
        self.refresh_appointments() 
    
    def refresh_patient_list(self):
        """Обновление списка пациентов"""
        self.patient_combo.clear()
        self.patient_combo.addItem("Все пациенты", None)
        
        patients = self.db.get_all_patients()
        for patient in patients:
            self.patient_combo.addItem(f"{patient[1]} ({patient[2]})", patient[0])
    
    def refresh_analysis_types(self):
        """Обновление списка типов анализов"""
        self.analysis_type_combo.clear()
        self.analysis_type_combo.addItem("Все типы", None)
        
        analysis_types = self.db.get_all_analysis_types()
        for analysis_type in analysis_types:
            self.analysis_type_combo.addItem(analysis_type[1], analysis_type[0])
    
    def refresh_doctor_list(self):
        """Обновление списка врачей"""
        self.doctor_combo.clear()
        self.doctor_combo.addItem("Все врачи", None)
        
        doctors = self.db.get_doctors()
        for doctor in doctors:
            self.doctor_combo.addItem(doctor[2], doctor[0])
    
    def refresh_analysis_results(self):
        """Обновление списка анализов"""
        patient_id = self.patient_combo.currentData()
        analysis_type_id = self.analysis_type_combo.currentData()
        from_date = self.analysis_from_date.date().toString("yyyy-MM-dd")
        to_date = self.analysis_to_date.date().toString("yyyy-MM-dd")
        
        # Получаем результаты анализов
        results = self.db.get_analysis_results(
            patient_id=patient_id,
            analysis_type_id=analysis_type_id,
            from_date=from_date,
            to_date=to_date
        )
        
        # Очищаем таблицу
        self.analysis_table.setRowCount(0)
        
        # Заполняем таблицу
        for row, result in enumerate(results):
            result_id, patient_name, birth_date, analysis_type, date_taken, lab_tech, status = result
            
            self.analysis_table.insertRow(row)
            self.analysis_table.setItem(row, 0, QTableWidgetItem(date_taken))
            self.analysis_table.setItem(row, 1, QTableWidgetItem(patient_name))
            self.analysis_table.setItem(row, 2, QTableWidgetItem(analysis_type))
            self.analysis_table.setItem(row, 3, QTableWidgetItem(status))
            self.analysis_table.setItem(row, 4, QTableWidgetItem(lab_tech))
            
            # Кнопки для работы с документами
            doc_widget = QWidget()
            doc_layout = QHBoxLayout(doc_widget)
            doc_layout.setContentsMargins(0, 0, 0, 0)
            
            view_button = QPushButton("Просмотр")
            view_button.setProperty("result_id", result_id)
            view_button.clicked.connect(self.view_analysis_result)
            
            export_button = QPushButton("Экспорт")
            export_button.setProperty("result_id", result_id)
            export_button.clicked.connect(self.export_analysis_to_doc)
            
            doc_layout.addWidget(view_button)
            doc_layout.addWidget(export_button)
            
            self.analysis_table.setCellWidget(row, 5, doc_widget)
            
            # Кнопка отправки по email
            email_button = QPushButton("Отправить")
            email_button.setProperty("result_id", result_id)
            email_button.clicked.connect(self.send_analysis_by_email)
            
            self.analysis_table.setCellWidget(row, 6, email_button)
        
        # Растягиваем колонки по содержимому
        self.analysis_table.resizeColumnsToContents()
    
    def clear_analysis_filters(self):
        """Сброс фильтров анализов"""
        self.patient_combo.setCurrentIndex(0)
        self.analysis_type_combo.setCurrentIndex(0)
        self.analysis_from_date.setDate(QDate.currentDate().addDays(-30))
        self.analysis_to_date.setDate(QDate.currentDate())
        self.refresh_analysis_results()
    
    def refresh_patients(self):
        """Обновление списка пациентов"""
        # Получаем список пациентов
        patients = self.db.get_all_patients()
        
        # Очищаем таблицу
        self.patients_table.setRowCount(0)
        
        # Заполняем таблицу
        for row, patient in enumerate(patients):
            patient_id, full_name, birth_date, gender, phone, email, address = patient
            
            self.patients_table.insertRow(row)
            self.patients_table.setItem(row, 0, QTableWidgetItem(full_name))
            self.patients_table.setItem(row, 1, QTableWidgetItem(birth_date))
            self.patients_table.setItem(row, 2, QTableWidgetItem(gender))
            self.patients_table.setItem(row, 3, QTableWidgetItem(phone if phone else ""))
            self.patients_table.setItem(row, 4, QTableWidgetItem(email if email else ""))
            self.patients_table.setItem(row, 5, QTableWidgetItem(address if address else ""))
            
            # Кнопки действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_button = QPushButton("Изменить")
            edit_button.setProperty("patient_id", patient_id)
            edit_button.clicked.connect(self.edit_patient_dialog)
            
            delete_button = QPushButton("Удалить")
            delete_button.setProperty("patient_id", patient_id)
            delete_button.clicked.connect(self.delete_patient)
            
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            
            self.patients_table.setCellWidget(row, 6, actions_widget)
        
        # Растягиваем колонки по содержимому
        self.patients_table.resizeColumnsToContents()
    
    def refresh_appointments(self):
        """Обновление расписания"""
        doctor_id = self.doctor_combo.currentData()
        patient_id = self.appointment_patient_combo.currentData()
        from_date = self.appointment_from_date.date().toString("yyyy-MM-dd")
        to_date = self.appointment_to_date.date().toString("yyyy-MM-dd")
        
        # Получаем расписание
        appointments = self.db.get_appointments(
            doctor_id=doctor_id,
            patient_id=patient_id,
            from_date=from_date,
            to_date=to_date
        )
        
        # Очищаем таблицу
        self.appointments_table.setRowCount(0)
        
        # Заполняем таблицу
        for row, appointment in enumerate(appointments):
            appointment_id, patient_id, patient_name, doctor_id, doctor_name, appointment_date, appointment_time, status, notes = appointment
            
            self.appointments_table.insertRow(row)
            self.appointments_table.setItem(row, 0, QTableWidgetItem(appointment_date))
            self.appointments_table.setItem(row, 1, QTableWidgetItem(appointment_time))
            self.appointments_table.setItem(row, 2, QTableWidgetItem(patient_name))
            self.appointments_table.setItem(row, 3, QTableWidgetItem(doctor_name))
            self.appointments_table.setItem(row, 4, QTableWidgetItem(status))
            self.appointments_table.setItem(row, 5, QTableWidgetItem(notes if notes else ""))
            
            # Кнопки действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_button = QPushButton("Изменить")
            edit_button.setProperty("appointment_id", appointment_id)
            edit_button.clicked.connect(self.edit_appointment_dialog)
            
            delete_button = QPushButton("Удалить")
            delete_button.setProperty("appointment_id", appointment_id)
            delete_button.clicked.connect(self.delete_appointment)
            
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            
            self.appointments_table.setCellWidget(row, 6, actions_widget)
        
        # Растягиваем колонки по содержимому
        self.appointments_table.resizeColumnsToContents()
    
    def clear_appointments_filters(self):
        """Сброс фильтров расписания"""
        self.doctor_combo.setCurrentIndex(0)
        self.appointment_patient_combo.setCurrentIndex(0)
        self.appointment_from_date.setDate(QDate.currentDate())
        self.appointment_to_date.setDate(QDate.currentDate().addDays(7))
        self.refresh_appointments()
    
    def view_analysis_result(self):
        """Просмотр результата анализа"""
        # Получаем ID результата из отправителя
        sender = self.sender()
        result_id = sender.property("result_id")
        
        # Получаем детали результата
        result_details = self.db.get_analysis_result_details(result_id)
        
        if result_details:
            # Создаем сообщение с результатами
            msg = QMessageBox(self)
            msg.setWindowTitle("Результаты анализа")
            msg.setIcon(QMessageBox.Information)
            
            # Формируем текст сообщения
            text = f"<b>Пациент:</b> {result_details['patient']['full_name']}<br>"
            text += f"<b>Дата рождения:</b> {result_details['patient']['birth_date']}<br>"
            text += f"<b>Тип анализа:</b> {result_details['analysis_type']['name']}<br>"
            text += f"<b>Дата взятия:</b> {result_details['date_taken']}<br>"
            text += f"<b>Лаборант:</b> {result_details['lab_technician']}<br>"
            text += f"<b>Статус:</b> {result_details['status']}<br><br>"
            
            text += "<b>Результаты:</b><br>"
            for param in result_details['parameters']:
                normal_range = f"{param['normal_min']} - {param['normal_max']}" if param['normal_min'] is not None and param['normal_max'] is not None else "не определена"
                
                if param['is_normal'] is not None:
                    if param['is_normal']:
                        color = "green"
                    else:
                        color = "red"
                    text += f"• {param['name']}: <span style='color:{color};font-weight:bold;'>{param['value']}</span> {param['unit']} (норма: {normal_range})<br>"
                else:
                    text += f"• {param['name']}: <b>{param['value']}</b> {param['unit']} (норма: {normal_range})<br>"
            
            msg.setText(text)
            msg.setTextFormat(Qt.RichText)
            
            # Показываем сообщение
            msg.exec_()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить результаты анализа")
    
    def export_analysis_to_doc(self):
        """Экспорт результата анализа в документ Word"""
        # Получаем ID результата из отправителя
        sender = self.sender()
        result_id = sender.property("result_id")
        
        # Получаем детали результата
        result_details = self.db.get_analysis_result_details(result_id)
        
        if result_details:
            try:
                # Генерируем документ
                file_path = self.document_generator.generate_analysis_report(result_details)
                
                # Показываем сообщение об успехе
                QMessageBox.information(self, "Успешно", f"Документ сохранен:\n{file_path}")
                
                # Предлагаем открыть документ
                reply = QMessageBox.question(self, "Открыть документ", 
                                           "Хотите открыть сгенерированный документ?",
                                           QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    import subprocess
                    import platform
                    
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.call(('open', file_path))
                    elif platform.system() == 'Windows':  # Windows
                        os.startfile(file_path)
                    else:  # Linux и другие Unix-системы
                        subprocess.call(('xdg-open', file_path))
            
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать документ: {str(e)}")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить результаты анализа")
    
    def send_analysis_by_email(self):
        """Отправка результата анализа по email"""
        # Получаем ID результата из отправителя
        sender = self.sender()
        result_id = sender.property("result_id")
        
        # Получаем детали результата
        result_details = self.db.get_analysis_result_details(result_id)
        
        if not result_details:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить результаты анализа")
            return
        
        # Получаем информацию о пациенте, включая email
        patient_id = result_details['patient']['id']
        patient_data = self.db.get_patient(patient_id)
        
        if not patient_data or not patient_data[4]:  # Проверка наличия email (индекс 4)
            QMessageBox.warning(self, "Ошибка", "У пациента не указан email")
            return
        
        try:
            # Генерируем документ
            file_path = self.document_generator.generate_analysis_report(result_details)
            
            # Отправляем email
            sent = self.email_sender.send_analysis_results(
                patient_email=patient_data[4],
                patient_name=patient_data[1],
                analysis_type=result_details['analysis_type']['name'],
                attachment_path=file_path
            )
            
            if sent:
                QMessageBox.information(self, "Успешно", "Результаты анализа отправлены на email пациента")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось отправить email")
        
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка отправки: {str(e)}")
    
    def add_patient_dialog(self):
        """Диалог добавления нового пациента"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление пациента")
        dialog.setMinimumWidth(400)
        
        # Макет диалога
        layout = QVBoxLayout(dialog)
        
        # Форма
        form_layout = QFormLayout()
        
        # Поля для ввода данных
        full_name_edit = QLineEdit()
        
        birth_date_edit = QDateEdit()
        birth_date_edit.setDate(QDate.currentDate())
        birth_date_edit.setCalendarPopup(True)
        
        gender_group = QButtonGroup(dialog)
        male_radio = QRadioButton("Мужской")
        female_radio = QRadioButton("Женский")
        male_radio.setChecked(True)
        gender_group.addButton(male_radio)
        gender_group.addButton(female_radio)
        
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(male_radio)
        gender_layout.addWidget(female_radio)
        
        phone_edit = QLineEdit()
        email_edit = QLineEdit()
        address_edit = QLineEdit()
        
        # Добавление полей в форму
        form_layout.addRow("ФИО:", full_name_edit)
        form_layout.addRow("Дата рождения:", birth_date_edit)
        form_layout.addRow("Пол:", gender_layout)
        form_layout.addRow("Телефон:", phone_edit)
        form_layout.addRow("Email:", email_edit)
        form_layout.addRow("Адрес:", address_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Привязка событий
        save_button.clicked.connect(lambda: self.save_patient(
            dialog,
            full_name_edit.text(),
            birth_date_edit.date().toString("yyyy-MM-dd"),
            "Мужской" if male_radio.isChecked() else "Женский",
            phone_edit.text(),
            email_edit.text(),
            address_edit.text()
        ))
        cancel_button.clicked.connect(dialog.reject)
        
        # Показываем диалог
        dialog.exec_()
    
    def save_patient(self, dialog, full_name, birth_date, gender, phone, email, address):
        """Сохранение нового пациента"""
        if not full_name:
            QMessageBox.warning(self, "Ошибка", "Введите ФИО пациента")
            return
        
        # Добавляем пациента
        self.db.add_patient(full_name, birth_date, gender, phone, email, address)
        
        # Обновляем списки пациентов
        self.refresh_patients()
        self.refresh_patient_list()
        
        # Закрываем диалог
        dialog.accept()
    
    def edit_patient_dialog(self):
        """Диалог редактирования пациента"""
        # Получаем ID пациента из отправителя
        sender = self.sender()
        patient_id = sender.property("patient_id")
        
        # Получаем данные пациента
        patient_data = self.db.get_patient(patient_id)
        
        if not patient_data:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные пациента")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Редактирование пациента: {patient_data[1]}")
        dialog.setMinimumWidth(400)
        
        # Макет диалога
        layout = QVBoxLayout(dialog)
        
        # Форма
        form_layout = QFormLayout()
        
        # Поля для ввода данных
        full_name_edit = QLineEdit(patient_data[1])
        
        birth_date_edit = QDateEdit()
        birth_date_edit.setDate(QDate.fromString(patient_data[2], "yyyy-MM-dd"))
        birth_date_edit.setCalendarPopup(True)
        
        gender_group = QButtonGroup(dialog)
        male_radio = QRadioButton("Мужской")
        female_radio = QRadioButton("Женский")
        if patient_data[3] == "Мужской":
            male_radio.setChecked(True)
        else:
            female_radio.setChecked(True)
        gender_group.addButton(male_radio)
        gender_group.addButton(female_radio)
        
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(male_radio)
        gender_layout.addWidget(female_radio)
        
        phone_edit = QLineEdit(patient_data[4] if patient_data[4] else "")
        email_edit = QLineEdit(patient_data[5] if patient_data[5] else "")
        address_edit = QLineEdit(patient_data[6] if patient_data[6] else "")
        
        # Добавление полей в форму
        form_layout.addRow("ФИО:", full_name_edit)
        form_layout.addRow("Дата рождения:", birth_date_edit)
        form_layout.addRow("Пол:", gender_layout)
        form_layout.addRow("Телефон:", phone_edit)
        form_layout.addRow("Email:", email_edit)
        form_layout.addRow("Адрес:", address_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Привязка событий
        save_button.clicked.connect(lambda: self.update_patient(
            dialog,
            patient_id,
            full_name_edit.text(),
            birth_date_edit.date().toString("yyyy-MM-dd"),
            "Мужской" if male_radio.isChecked() else "Женский",
            phone_edit.text(),
            email_edit.text(),
            address_edit.text()
        ))
        cancel_button.clicked.connect(dialog.reject)
        
        # Показываем диалог
        dialog.exec_()
    
    def update_patient(self, dialog, patient_id, full_name, birth_date, gender, phone, email, address):
        """Обновление данных пациента"""
        if not full_name:
            QMessageBox.warning(self, "Ошибка", "Введите ФИО пациента")
            return
        
        # Обновляем данные пациента
        self.db.update_patient(patient_id, full_name, birth_date, gender, phone, email, address)
        
        # Обновляем списки пациентов
        self.refresh_patients()
        self.refresh_patient_list()
        
        # Закрываем диалог
        dialog.accept()
    
    def delete_patient(self):
        """Удаление пациента"""
        # Получаем ID пациента из отправителя
        sender = self.sender()
        patient_id = sender.property("patient_id")
        
        # Запрашиваем подтверждение
        reply = QMessageBox.question(self, "Подтверждение удаления", 
                                   "Вы уверены, что хотите удалить этого пациента?\nЭто действие нельзя отменить.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Удаляем пациента
            self.db.delete_patient(patient_id)
            
            # Обновляем списки пациентов
            self.refresh_patients()
            self.refresh_patient_list()
    
    def add_appointment_dialog(self):
        """Диалог добавления нового приема"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление приема")
        dialog.setMinimumWidth(400)
        
        # Макет диалога
        layout = QVBoxLayout(dialog)
        
        # Форма
        form_layout = QFormLayout()
        
        # Выбор пациента
        patient_combo = QComboBox()
        patient_combo.setMinimumWidth(250)
        patients = self.db.get_all_patients()
        for patient in patients:
            patient_combo.addItem(f"{patient[1]} ({patient[2]})", patient[0])
        
        # Выбор врача
        doctor_combo = QComboBox()
        doctor_combo.setMinimumWidth(250)
        doctors = self.db.get_doctors()
        for doctor in doctors:
            doctor_combo.addItem(doctor[2], doctor[0])
        
        # Выбор даты
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        
        # Выбор времени
        time_edit = QTimeEdit()
        time_edit.setTime(QTime(9, 0))
        
        # Статус
        status_combo = QComboBox()
        status_combo.addItem("запланирован")
        status_combo.addItem("завершен")
        status_combo.addItem("отменен")
        
        # Примечания
        notes_edit = QLineEdit()
        
        # Добавление полей в форму
        form_layout.addRow("Пациент:", patient_combo)
        form_layout.addRow("Врач:", doctor_combo)
        form_layout.addRow("Дата:", date_edit)
        form_layout.addRow("Время:", time_edit)
        form_layout.addRow("Статус:", status_combo)
        form_layout.addRow("Примечания:", notes_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Привязка событий
        save_button.clicked.connect(lambda: self.save_appointment(
            dialog, 
            patient_combo.currentData(), 
            doctor_combo.currentData(),
            date_edit.date().toString("yyyy-MM-dd"),
            time_edit.time().toString("HH:mm"),
            status_combo.currentText(),
            notes_edit.text()
        ))
        cancel_button.clicked.connect(dialog.reject)
        
        # Показываем диалог
        dialog.exec_()
    
    def save_appointment(self, dialog, patient_id, doctor_id, appointment_date, appointment_time, status, notes):
        """Сохранение нового приема"""
        if not patient_id:
            QMessageBox.warning(self, "Ошибка", "Выберите пациента")
            return
        
        if not doctor_id:
            QMessageBox.warning(self, "Ошибка", "Выберите врача")
            return
        
        # Добавляем прием
        self.db.add_appointment(patient_id, doctor_id, appointment_date, appointment_time, status, notes)
        
        # Обновляем расписание
        self.refresh_appointments()
        
        # Закрываем диалог
        dialog.accept()
    
    def edit_appointment_dialog(self):
        """Диалог редактирования приема"""
        # Получаем ID приема из отправителя
        sender = self.sender()
        appointment_id = sender.property("appointment_id")
        
        # В этой версии просто показываем диалог добавления нового приема
        # В реальном приложении здесь нужно загрузить данные текущего приема и показать их в диалоге
        self.add_appointment_dialog()
    
    def delete_appointment(self):
        """Удаление приема"""
        # Получаем ID приема из отправителя
        sender = self.sender()
        appointment_id = sender.property("appointment_id")
        
        # Запрашиваем подтверждение
        reply = QMessageBox.question(self, "Подтверждение удаления", 
                                   "Вы уверены, что хотите удалить этот прием?\nЭто действие нельзя отменить.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # В этой версии просто обновляем расписание
            # В реальном приложении здесь нужно удалить прием из базы данных
            self.refresh_appointments() 