from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QDateEdit, QStackedWidget, QGroupBox, 
                             QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QScrollArea)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime

from app.database.database import Database
from app.models.models import UserRole, AnalysisResult

class LabTechnicianWindow(QMainWindow):
    """Окно интерфейса лаборанта"""
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        # Настройка окна
        self.setWindowTitle(f"Лаборант - {self.user_data['full_name']}")
        self.setMinimumSize(800, 600)
        
        # Основной виджет и макет
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Заголовок
        header_label = QLabel("Система ввода результатов анализов")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Поле выбора пациента
        patient_group = QGroupBox("Выбор пациента и типа анализа")
        patient_layout = QVBoxLayout()
        
        # Поле выбора пациента
        patient_selection_layout = QHBoxLayout()
        patient_label = QLabel("Пациент:")
        self.patient_combo = QComboBox()
        self.refresh_patient_list()  # Заполняем список пациентов
        
        patient_selection_layout.addWidget(patient_label)
        patient_selection_layout.addWidget(self.patient_combo, 1)
        patient_layout.addLayout(patient_selection_layout)
        
        # Поле выбора типа анализа
        analysis_selection_layout = QHBoxLayout()
        analysis_label = QLabel("Тип анализа:")
        self.analysis_combo = QComboBox()
        self.refresh_analysis_types()  # Заполняем список типов анализа
        
        analysis_selection_layout.addWidget(analysis_label)
        analysis_selection_layout.addWidget(self.analysis_combo, 1)
        patient_layout.addLayout(analysis_selection_layout)
        
        # Поле выбора даты
        date_selection_layout = QHBoxLayout()
        date_label = QLabel("Дата анализа:")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        
        date_selection_layout.addWidget(date_label)
        date_selection_layout.addWidget(self.date_edit, 1)
        patient_layout.addLayout(date_selection_layout)
        
        # Кнопка начать заполнение
        start_button_layout = QHBoxLayout()
        start_button_layout.addStretch()
        
        self.start_button = QPushButton("Начать заполнение")
        self.start_button.setFixedSize(150, 40)
        self.start_button.clicked.connect(self.show_analysis_form)
        
        start_button_layout.addWidget(self.start_button)
        start_button_layout.addStretch()
        
        patient_layout.addLayout(start_button_layout)
        patient_group.setLayout(patient_layout)
        
        main_layout.addWidget(patient_group)
        
        # Группа для формы анализа (изначально скрыта)
        self.analysis_form_group = QGroupBox("Заполнение результатов анализа")
        self.analysis_form_group.setVisible(False)
        analysis_form_layout = QVBoxLayout()
        
        # Информация о пациенте и анализе
        info_layout = QFormLayout()
        self.patient_info_label = QLabel()
        self.analysis_type_label = QLabel()
        self.date_info_label = QLabel()
        
        info_layout.addRow("Пациент:", self.patient_info_label)
        info_layout.addRow("Тип анализа:", self.analysis_type_label)
        info_layout.addRow("Дата:", self.date_info_label)
        
        analysis_form_layout.addLayout(info_layout)
        
        # Контейнер для параметров анализа
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        parameters_widget = QWidget()
        self.parameters_layout = QFormLayout(parameters_widget)
        scroll_area.setWidget(parameters_widget)
        
        analysis_form_layout.addWidget(QLabel("Параметры анализа:"))
        analysis_form_layout.addWidget(scroll_area)
        
        # Кнопка сохранения
        save_button_layout = QHBoxLayout()
        save_button_layout.addStretch()
        
        self.save_button = QPushButton("Сохранить")
        self.save_button.setFixedSize(120, 40)
        self.save_button.clicked.connect(self.save_analysis_results)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setFixedSize(120, 40)
        self.cancel_button.clicked.connect(self.cancel_analysis)
        
        save_button_layout.addWidget(self.cancel_button)
        save_button_layout.addWidget(self.save_button)
        
        analysis_form_layout.addLayout(save_button_layout)
        self.analysis_form_group.setLayout(analysis_form_layout)
        
        main_layout.addWidget(self.analysis_form_group)
        
        # Группа для истории анализов
        history_group = QGroupBox("История заполненных анализов")
        history_layout = QVBoxLayout()
        
        # Таблица с историей
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Дата", "Пациент", "Тип анализа", "Статус", ""])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        
        main_layout.addWidget(history_group)
        
        # Загружаем историю анализов
        self.refresh_history()
        
        # Устанавливаем центральный виджет
        self.setCentralWidget(central_widget)
    
    def refresh_patient_list(self):
        """Обновление списка пациентов"""
        self.patient_combo.clear()
        patients = self.db.get_all_patients()
        
        for patient in patients:
            self.patient_combo.addItem(f"{patient[1]} ({patient[2]})", patient[0])
    
    def refresh_analysis_types(self):
        """Обновление списка типов анализов"""
        self.analysis_combo.clear()
        analysis_types = self.db.get_all_analysis_types()
        
        for analysis_type in analysis_types:
            self.analysis_combo.addItem(analysis_type[1], analysis_type[0])
    
    def show_analysis_form(self):
        """Показ формы для заполнения результатов анализа"""
        # Проверяем, выбран ли пациент и тип анализа
        if self.patient_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите пациента")
            return
        
        if self.analysis_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите тип анализа")
            return
        
        # Получаем выбранные значения
        patient_id = self.patient_combo.currentData()
        patient_name = self.patient_combo.currentText()
        analysis_type_id = self.analysis_combo.currentData()
        analysis_type_name = self.analysis_combo.currentText()
        date_taken = self.date_edit.date().toString("yyyy-MM-dd")
        
        # Отображаем информацию
        self.patient_info_label.setText(patient_name)
        self.analysis_type_label.setText(analysis_type_name)
        self.date_info_label.setText(date_taken)
        
        # Очищаем предыдущие поля
        self.clear_parameters_layout()
        
        # Получаем параметры для выбранного типа анализа
        parameters = self.db.get_analysis_parameters(analysis_type_id)
        
        # Создаем поля для ввода значений параметров
        for param in parameters:
            param_id, param_name, param_unit, normal_min, normal_max = param
            
            # Создаем поле для значения
            value_input = QDoubleSpinBox()
            value_input.setDecimals(2)
            value_input.setMinimum(0)
            value_input.setMaximum(1000)
            value_input.setProperty("param_id", param_id)
            
            # Создаем метку с названием и нормой
            normal_range = ""
            if normal_min is not None and normal_max is not None:
                normal_range = f" (норма: {normal_min} - {normal_max} {param_unit})"
            
            label = QLabel(f"{param_name}{normal_range}")
            
            # Добавляем в форму
            self.parameters_layout.addRow(label, value_input)
        
        # Показываем форму
        self.analysis_form_group.setVisible(True)
    
    def clear_parameters_layout(self):
        """Очистка формы параметров"""
        while self.parameters_layout.count():
            item = self.parameters_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def save_analysis_results(self):
        """Сохранение результатов анализа"""
        # Получаем выбранные значения
        patient_id = self.patient_combo.currentData()
        analysis_type_id = self.analysis_combo.currentData()
        date_taken = self.date_edit.date().toString("yyyy-MM-dd")
        
        # Создаем результат анализа
        analysis_result_id = self.db.add_analysis_result(
            patient_id, 
            analysis_type_id, 
            date_taken, 
            self.user_data['id']
        )
        
        # Сохраняем значения параметров
        for row in range(self.parameters_layout.rowCount()):
            # Получаем виджет значения (в каждой строке два виджета: метка и поле ввода)
            value_widget = self.parameters_layout.itemAt(row * 2 + 1).widget()
            
            if isinstance(value_widget, QDoubleSpinBox):
                param_id = value_widget.property("param_id")
                value = value_widget.value()
                
                # Сохраняем значение параметра
                self.db.add_parameter_value(analysis_result_id, param_id, value)
        
        # Показываем сообщение об успехе
        QMessageBox.information(self, "Успешно", "Результаты анализа сохранены")
        
        # Обновляем историю
        self.refresh_history()
        
        # Скрываем форму
        self.analysis_form_group.setVisible(False)
        self.clear_parameters_layout()
    
    def cancel_analysis(self):
        """Отмена заполнения анализа"""
        self.analysis_form_group.setVisible(False)
        self.clear_parameters_layout()
    
    def refresh_history(self):
        """Обновление истории анализов"""
        # Получаем историю анализов для текущего лаборанта
        results = self.db.get_analysis_results(lab_technician_id=self.user_data['id'])
        
        # Очищаем таблицу
        self.history_table.setRowCount(0)
        
        # Заполняем таблицу
        for row, result in enumerate(results):
            result_id, patient_name, birth_date, analysis_type, date_taken, lab_tech, status = result
            
            self.history_table.insertRow(row)
            self.history_table.setItem(row, 0, QTableWidgetItem(date_taken))
            self.history_table.setItem(row, 1, QTableWidgetItem(patient_name))
            self.history_table.setItem(row, 2, QTableWidgetItem(analysis_type))
            self.history_table.setItem(row, 3, QTableWidgetItem(status))
            
            # Кнопка просмотра
            view_button = QPushButton("Просмотр")
            view_button.setProperty("result_id", result_id)
            view_button.clicked.connect(self.view_result)
            
            self.history_table.setCellWidget(row, 4, view_button)
    
    def view_result(self):
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
                text += f"• {param['name']}: <b>{param['value']}</b> {param['unit']} (норма: {normal_range})<br>"
            
            msg.setText(text)
            msg.setTextFormat(Qt.RichText)
            
            # Показываем сообщение
            msg.exec_()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить результаты анализа") 