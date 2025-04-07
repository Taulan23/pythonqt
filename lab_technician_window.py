from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QComboBox, QPushButton,
                               QVBoxLayout, QHBoxLayout, QMessageBox, QFormLayout, 
                               QTableWidget, QTableWidgetItem, QLineEdit, QDialog,
                               QScrollArea, QGridLayout, QGroupBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
import sys
import json
from datetime import datetime

from database_connection import db

class AnalysisEntryForm(QDialog):
    """Диалоговое окно для ввода результатов анализа"""
    
    def __init__(self, patient_name, analysis_type, parameters, parent=None):
        super().__init__(parent)
        self.patient_name = patient_name
        self.analysis_type = analysis_type
        self.parameters = parameters
        self.parameter_inputs = {}  # Словарь для хранения полей ввода
        
        self.setWindowTitle(f"Ввод результатов анализа: {analysis_type}")
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса формы ввода"""
        layout = QVBoxLayout()
        
        # Заголовок с информацией
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_frame.setStyleSheet("background-color: #f8f9fa;")
        info_layout = QVBoxLayout(info_frame)
        
        title_label = QLabel(f"Пациент: {self.patient_name}")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(title_label)
        
        analysis_label = QLabel(f"Тип анализа: {self.analysis_type}")
        analysis_label.setFont(QFont("Arial", 10))
        info_layout.addWidget(analysis_label)
        
        date_label = QLabel(f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
        date_label.setFont(QFont("Arial", 10))
        info_layout.addWidget(date_label)
        
        layout.addWidget(info_frame)
        
        # Создание формы с полями для параметров анализа
        form_group = QGroupBox("Заполните значения параметров:")
        form_layout = QFormLayout()
        
        for param in self.parameters:
            param_input = QLineEdit()
            param_input.setPlaceholderText(f"Введите значение для {param}")
            form_layout.addRow(f"{param}:", param_input)
            self.parameter_inputs[param] = param_input
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Сохранить")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        save_button.clicked.connect(self.save_analysis)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def save_analysis(self):
        """Сохранение результатов анализа"""
        # Проверка заполнения всех полей
        empty_fields = []
        for param, input_field in self.parameter_inputs.items():
            if not input_field.text().strip():
                empty_fields.append(param)
        
        if empty_fields:
            QMessageBox.warning(
                self,
                "Недостаточно данных",
                f"Пожалуйста, заполните все поля. Не заполнены: {', '.join(empty_fields)}"
            )
            return
        
        # Сбор данных из полей ввода
        result_data = {}
        for param, input_field in self.parameter_inputs.items():
            result_data[param] = input_field.text().strip()
        
        # Возвращаем результаты
        self.result_data = result_data
        self.accept()

class LabTechnicianWindow(QMainWindow):
    """Главное окно интерфейса лаборанта"""
    logout_signal = Signal()
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        
        self.setWindowTitle(f"Медицинский центр - Лаборант: {user_data['full_name']}")
        self.setMinimumSize(800, 600)
        
        # Загрузка данных для работы
        self.patients = db.get_all_patients()
        self.analysis_types = db.get_all_analysis_types()
        
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
        
        user_info = QLabel(f"Пользователь: {self.user_data['full_name']}")
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
        
        # Панель выбора пациента и типа анализа
        selection_layout = QHBoxLayout()
        
        # Выбор пациента
        patient_group = QGroupBox("Выбор пациента")
        patient_layout = QVBoxLayout()
        
        self.patient_combo = QComboBox()
        for patient in self.patients:
            self.patient_combo.addItem(patient['full_name'], patient['id'])
        
        patient_layout.addWidget(self.patient_combo)
        
        # Добавляем фильтр для отображения пациентов без анализов
        filter_layout = QHBoxLayout()
        
        self.show_all_patients_button = QPushButton("Все пациенты")
        self.show_all_patients_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.show_all_patients_button.clicked.connect(self.show_all_patients)
        filter_layout.addWidget(self.show_all_patients_button)
        
        self.show_patients_without_analysis_button = QPushButton("Пациенты без анализов")
        self.show_patients_without_analysis_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.show_patients_without_analysis_button.clicked.connect(self.show_patients_without_analysis)
        filter_layout.addWidget(self.show_patients_without_analysis_button)
        
        patient_layout.addLayout(filter_layout)
        patient_group.setLayout(patient_layout)
        selection_layout.addWidget(patient_group)
        
        # Выбор типа анализа
        analysis_group = QGroupBox("Выбор типа анализа")
        analysis_layout = QVBoxLayout()
        
        self.analysis_combo = QComboBox()
        for analysis in self.analysis_types:
            self.analysis_combo.addItem(analysis['name'], analysis['id'])
        
        analysis_layout.addWidget(self.analysis_combo)
        analysis_group.setLayout(analysis_layout)
        selection_layout.addWidget(analysis_group)
        
        main_layout.addLayout(selection_layout)
        
        # Кнопка начала заполнения анализа
        start_button = QPushButton("Начать заполнение")
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
        """)
        start_button.clicked.connect(self.start_analysis_entry)
        main_layout.addWidget(start_button)
        
        # Таблица с ранее введенными анализами
        history_group = QGroupBox("История анализов")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Пациент", "Тип анализа", "Дата", "Статус", "Действия"
        ])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        
        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)
        
        # Загрузка истории анализов
        self.load_analysis_history()
    
    def load_analysis_history(self):
        """Загрузка истории анализов, выполненных текущим лаборантом"""
        analysis_results = db.fetch_all("""
            SELECT ar.*, p.full_name as patient_name, at.name as analysis_name 
            FROM analysis_results ar
            JOIN patients p ON ar.patient_id = p.id
            JOIN analysis_types at ON ar.analysis_type_id = at.id
            WHERE ar.lab_user_id = ?
            ORDER BY ar.result_date DESC
        """, (self.user_data['id'],))
        
        self.history_table.setRowCount(len(analysis_results))
        
        for row, result in enumerate(analysis_results):
            self.history_table.setItem(row, 0, QTableWidgetItem(result['patient_name']))
            self.history_table.setItem(row, 1, QTableWidgetItem(result['analysis_name']))
            
            # Корректная обработка даты (может быть строкой)
            result_date = result['result_date']
            if result_date:
                # Если дата уже в строковом формате, используем её как есть
                # Иначе форматируем с помощью strftime
                if isinstance(result_date, str):
                    date_str = result_date
                else:
                    date_str = result_date.strftime('%d.%m.%Y %H:%M')
            else:
                date_str = ""
                
            self.history_table.setItem(row, 2, QTableWidgetItem(date_str))
            
            status_item = QTableWidgetItem(result['status'])
            if result['status'] == 'completed':
                status_item.setText("Выполнен")
            elif result['status'] == 'pending':
                status_item.setText("В обработке")
            elif result['status'] == 'sent':
                status_item.setText("Отправлен")
            
            self.history_table.setItem(row, 3, status_item)
            
            view_button = QPushButton("Просмотр")
            view_button.clicked.connect(lambda checked, r=result: self.view_analysis_result(r))
            self.history_table.setCellWidget(row, 4, view_button)
    
    def start_analysis_entry(self):
        """Начало ввода результатов анализа"""
        # Получение выбранного пациента и типа анализа
        patient_id = self.patient_combo.currentData()
        patient_name = self.patient_combo.currentText()
        
        analysis_id = self.analysis_combo.currentData()
        analysis_name = self.analysis_combo.currentText()
        
        # Получение параметров выбранного типа анализа
        parameters = db.get_analysis_parameters(analysis_id)
        
        if not parameters:
            QMessageBox.warning(self, "Ошибка", "Для выбранного типа анализа не определены параметры")
            return
        
        # Открытие формы для ввода результатов
        entry_form = AnalysisEntryForm(patient_name, analysis_name, parameters, self)
        if entry_form.exec() == QDialog.Accepted:
            # Сохранение результатов в базу данных
            success = db.add_analysis_result(
                patient_id=patient_id,
                analysis_type_id=analysis_id,
                lab_user_id=self.user_data['id'],
                result_data=entry_form.result_data
            )
            
            if success:
                QMessageBox.information(
                    self, 
                    "Успех", 
                    "Результаты анализа успешно сохранены"
                )
                # Обновление истории анализов
                self.load_analysis_history()
            else:
                QMessageBox.critical(
                    self, 
                    "Ошибка", 
                    "Не удалось сохранить результаты анализа"
                )
    
    def view_analysis_result(self, result):
        """Просмотр результатов анализа"""
        try:
            # Попытка десериализации данных результата
            result_data = result['result_data']
            if isinstance(result_data, str):
                try:
                    result_data = json.loads(result_data)
                except json.JSONDecodeError:
                    pass
            
            # Формирование строки для отображения
            if isinstance(result_data, dict):
                result_text = "\n".join([f"{k}: {v}" for k, v in result_data.items()])
            else:
                result_text = str(result_data)
            
            # Корректная обработка даты (может быть строкой)
            result_date = result['result_date']
            if result_date:
                if isinstance(result_date, str):
                    date_str = result_date
                else:
                    date_str = result_date.strftime('%d.%m.%Y %H:%M')
            else:
                date_str = "Дата не указана"
                
            QMessageBox.information(
                self,
                f"Результаты анализа: {result['analysis_name']}",
                f"Пациент: {result['patient_name']}\n"
                f"Дата: {date_str}\n\n"
                f"Результаты:\n{result_text}"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Ошибка просмотра",
                f"Не удалось отобразить результаты анализа: {str(e)}"
            )
    
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

    def show_all_patients(self):
        """Показать всех пациентов в выпадающем списке"""
        self.patient_combo.clear()
        self.patients = db.get_all_patients()
        for patient in self.patients:
            self.patient_combo.addItem(patient['full_name'], patient['id'])
        
        QMessageBox.information(
            self,
            "Информация",
            f"Отображены все пациенты ({len(self.patients)})"
        )
    
    def show_patients_without_analysis(self):
        """Показать только пациентов, у которых нет анализов выбранного типа"""
        # Получаем ID выбранного типа анализа
        analysis_id = self.analysis_combo.currentData()
        analysis_name = self.analysis_combo.currentText()
        
        # Получаем пациентов без анализов данного типа
        patients_without_analysis = db.get_patients_without_analysis(analysis_id)
        
        # Обновляем выпадающий список
        self.patient_combo.clear()
        for patient in patients_without_analysis:
            self.patient_combo.addItem(patient['full_name'], patient['id'])
        
        QMessageBox.information(
            self,
            "Информация",
            f"Отображены пациенты, у которых нет анализа '{analysis_name}' ({len(patients_without_analysis)})"
        )


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Тестовый пользователь
    test_user = {
        'id': 3,
        'username': 'lab1',
        'full_name': 'Иванова Мария Петровна',
        'role': 'lab'
    }
    
    window = LabTechnicianWindow(test_user)
    window.show()
    
    sys.exit(app.exec()) 