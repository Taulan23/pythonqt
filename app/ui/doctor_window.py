from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTabWidget, QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QDateEdit, QGroupBox, QFormLayout, QMessageBox,
                             QSplitter, QLineEdit, QDialog, QTimeEdit)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime, timedelta

from app.database.database import Database
from app.models.models import UserRole

class DoctorWindow(QMainWindow):
    """Окно интерфейса врача"""
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        # Настройка окна
        self.setWindowTitle(f"Врач - {self.user_data['full_name']}")
        self.setMinimumSize(1000, 700)
        
        # Основной виджет и макет
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Заголовок
        header_label = QLabel(f"Добро пожаловать, {self.user_data['full_name']}")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Вкладки
        tab_widget = QTabWidget()
        
        # Вкладка "Расписание"
        schedule_tab = QWidget()
        schedule_layout = QVBoxLayout(schedule_tab)
        
        # Фильтры для расписания
        schedule_filters_group = QGroupBox("Фильтры")
        schedule_filters_layout = QHBoxLayout()
        
        # Выбор даты начала
        from_date_label = QLabel("С:")
        self.schedule_from_date = QDateEdit()
        self.schedule_from_date.setDate(QDate.currentDate())
        self.schedule_from_date.setCalendarPopup(True)
        
        # Выбор даты окончания
        to_date_label = QLabel("По:")
        self.schedule_to_date = QDateEdit()
        self.schedule_to_date.setDate(QDate.currentDate().addDays(7))
        self.schedule_to_date.setCalendarPopup(True)
        
        # Кнопка применения фильтров
        apply_schedule_filters_button = QPushButton("Применить")
        apply_schedule_filters_button.clicked.connect(self.refresh_schedule)
        
        # Кнопка очистки фильтров
        clear_schedule_filters_button = QPushButton("Сбросить")
        clear_schedule_filters_button.clicked.connect(self.clear_schedule_filters)
        
        # Размещение фильтров
        schedule_filters_layout.addWidget(from_date_label)
        schedule_filters_layout.addWidget(self.schedule_from_date)
        schedule_filters_layout.addWidget(to_date_label)
        schedule_filters_layout.addWidget(self.schedule_to_date)
        schedule_filters_layout.addStretch()
        schedule_filters_layout.addWidget(apply_schedule_filters_button)
        schedule_filters_layout.addWidget(clear_schedule_filters_button)
        
        schedule_filters_group.setLayout(schedule_filters_layout)
        schedule_layout.addWidget(schedule_filters_group)
        
        # Таблица расписания
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels([
            "Дата", "Время", "Пациент", "Статус", "Примечания", "Действия"
        ])
        self.schedule_table.horizontalHeader().setStretchLastSection(True)
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        schedule_layout.addWidget(self.schedule_table)
        
        # Кнопка добавления нового приема
        add_appointment_button = QPushButton("Добавить прием")
        add_appointment_button.clicked.connect(self.add_appointment_dialog)
        schedule_layout.addWidget(add_appointment_button)
        
        # Вкладка "Анализы"
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
        self.analysis_table.setColumnCount(6)
        self.analysis_table.setHorizontalHeaderLabels([
            "Дата", "Пациент", "Тип анализа", "Статус", "Лаборант", "Действия"
        ])
        self.analysis_table.horizontalHeader().setStretchLastSection(True)
        self.analysis_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        analysis_layout.addWidget(self.analysis_table)
        
        # Добавление вкладок
        tab_widget.addTab(schedule_tab, "Расписание")
        tab_widget.addTab(analysis_tab, "Анализы")
        
        main_layout.addWidget(tab_widget)
        
        # Установка центрального виджета
        self.setCentralWidget(central_widget)
        
        # Загрузка данных
        self.refresh_schedule()
        self.refresh_analysis_results()
    
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
    
    def refresh_schedule(self):
        """Обновление расписания"""
        from_date = self.schedule_from_date.date().toString("yyyy-MM-dd")
        to_date = self.schedule_to_date.date().toString("yyyy-MM-dd")
        
        # Получаем расписание
        appointments = self.db.get_appointments(
            doctor_id=self.user_data['id'],
            from_date=from_date,
            to_date=to_date
        )
        
        # Очищаем таблицу
        self.schedule_table.setRowCount(0)
        
        # Заполняем таблицу
        for row, appointment in enumerate(appointments):
            appointment_id, patient_id, patient_name, _, _, appointment_date, appointment_time, status, notes = appointment
            
            self.schedule_table.insertRow(row)
            self.schedule_table.setItem(row, 0, QTableWidgetItem(appointment_date))
            self.schedule_table.setItem(row, 1, QTableWidgetItem(appointment_time))
            self.schedule_table.setItem(row, 2, QTableWidgetItem(patient_name))
            self.schedule_table.setItem(row, 3, QTableWidgetItem(status))
            self.schedule_table.setItem(row, 4, QTableWidgetItem(notes if notes else ""))
            
            # Кнопки действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            if status == "запланирован":
                # Кнопка "Завершен"
                complete_button = QPushButton("Завершен")
                complete_button.setProperty("appointment_id", appointment_id)
                complete_button.clicked.connect(self.complete_appointment)
                actions_layout.addWidget(complete_button)
                
                # Кнопка "Отменен"
                cancel_button = QPushButton("Отменен")
                cancel_button.setProperty("appointment_id", appointment_id)
                cancel_button.clicked.connect(self.cancel_appointment)
                actions_layout.addWidget(cancel_button)
            else:
                # Кнопка просмотра
                view_button = QPushButton("Просмотр")
                view_button.setProperty("appointment_id", appointment_id)
                view_button.clicked.connect(self.view_appointment)
                actions_layout.addWidget(view_button)
            
            self.schedule_table.setCellWidget(row, 5, actions_widget)
        
        # Растягиваем колонки по содержимому
        self.schedule_table.resizeColumnsToContents()
    
    def clear_schedule_filters(self):
        """Сброс фильтров расписания"""
        self.schedule_from_date.setDate(QDate.currentDate())
        self.schedule_to_date.setDate(QDate.currentDate().addDays(7))
        self.refresh_schedule()
    
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
            
            # Кнопка просмотра
            view_button = QPushButton("Просмотр")
            view_button.setProperty("result_id", result_id)
            view_button.clicked.connect(self.view_analysis_result)
            
            self.analysis_table.setCellWidget(row, 5, view_button)
        
        # Растягиваем колонки по содержимому
        self.analysis_table.resizeColumnsToContents()
    
    def clear_analysis_filters(self):
        """Сброс фильтров анализов"""
        self.patient_combo.setCurrentIndex(0)
        self.analysis_type_combo.setCurrentIndex(0)
        self.analysis_from_date.setDate(QDate.currentDate().addDays(-30))
        self.analysis_to_date.setDate(QDate.currentDate())
        self.refresh_analysis_results()
    
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
            date_edit.date().toString("yyyy-MM-dd"),
            time_edit.time().toString("HH:mm"),
            status_combo.currentText(),
            notes_edit.text()
        ))
        cancel_button.clicked.connect(dialog.reject)
        
        # Показываем диалог
        dialog.exec_()
    
    def save_appointment(self, dialog, patient_id, appointment_date, appointment_time, status, notes):
        """Сохранение нового приема"""
        if not patient_id:
            QMessageBox.warning(self, "Ошибка", "Выберите пациента")
            return
        
        # Добавляем прием
        self.db.add_appointment(patient_id, self.user_data['id'], appointment_date, appointment_time, status, notes)
        
        # Обновляем расписание
        self.refresh_schedule()
        
        # Закрываем диалог
        dialog.accept()
    
    def complete_appointment(self):
        """Пометить прием как завершенный"""
        # Получаем ID приема из отправителя
        sender = self.sender()
        appointment_id = sender.property("appointment_id")
        
        # Обновляем статус
        self.db.update_appointment_status(appointment_id, "завершен")
        
        # Обновляем расписание
        self.refresh_schedule()
    
    def cancel_appointment(self):
        """Пометить прием как отмененный"""
        # Получаем ID приема из отправителя
        sender = self.sender()
        appointment_id = sender.property("appointment_id")
        
        # Обновляем статус
        self.db.update_appointment_status(appointment_id, "отменен")
        
        # Обновляем расписание
        self.refresh_schedule()
    
    def view_appointment(self):
        """Просмотр информации о приеме"""
        # Получаем ID приема из отправителя
        sender = self.sender()
        appointment_id = sender.property("appointment_id")
        
        # Здесь можно добавить просмотр детальной информации о приеме
        QMessageBox.information(self, "Информация", f"Просмотр информации о приеме #{appointment_id}") 