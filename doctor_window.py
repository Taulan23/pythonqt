from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QComboBox, QPushButton,
                               QVBoxLayout, QHBoxLayout, QMessageBox, QFormLayout, 
                               QTableWidget, QTableWidgetItem, QLineEdit, QDialog,
                               QTabWidget, QCalendarWidget, QDateEdit, QGroupBox,
                               QScrollArea, QFrame, QHeaderView)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QIcon, QColor
import sys
import json
from datetime import datetime

from database_connection import db

class AppointmentDetailsDialog(QDialog):
    """Диалоговое окно с деталями приема"""
    
    def __init__(self, appointment_data, parent=None):
        super().__init__(parent)
        self.appointment_data = appointment_data
        
        self.setWindowTitle("Детали приема")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout()
        
        # Информация о пациенте
        patient_group = QGroupBox("Информация о пациенте")
        patient_layout = QFormLayout()
        
        patient_name = QLabel(self.appointment_data.get('patient_name', ''))
        patient_name.setFont(QFont("Arial", 10, QFont.Bold))
        patient_layout.addRow("Пациент:", patient_name)
        
        # Получаем дополнительную информацию о пациенте
        patient_id = self.appointment_data.get('patient_id')
        if patient_id:
            patient_info = db.get_patient(patient_id)
            if patient_info:
                patient_layout.addRow("Дата рождения:", QLabel(patient_info.get('birth_date', '')))
                patient_layout.addRow("Телефон:", QLabel(patient_info.get('phone', '')))
                patient_layout.addRow("Email:", QLabel(patient_info.get('email', '')))
        
        patient_group.setLayout(patient_layout)
        layout.addWidget(patient_group)
        
        # Информация о приеме
        appointment_group = QGroupBox("Информация о приеме")
        appointment_layout = QFormLayout()
        
        date_time = QLabel(self.appointment_data.get('appointment_date', ''))
        appointment_layout.addRow("Дата и время:", date_time)
        
        status_label = QLabel(self.get_status_text(self.appointment_data.get('status', '')))
        appointment_layout.addRow("Статус:", status_label)
        
        notes_label = QLabel(self.appointment_data.get('notes', ''))
        notes_label.setWordWrap(True)
        appointment_layout.addRow("Примечания:", notes_label)
        
        appointment_group.setLayout(appointment_layout)
        layout.addWidget(appointment_group)
        
        # Получаем анализы пациента, если есть
        patient_id = self.appointment_data.get('patient_id')
        if patient_id:
            analysis_results = db.get_patient_analysis_results(patient_id)
            if analysis_results:
                analysis_group = QGroupBox("Анализы пациента")
                analysis_layout = QVBoxLayout()
                
                analysis_table = QTableWidget()
                analysis_table.setColumnCount(3)
                analysis_table.setHorizontalHeaderLabels(["Тип анализа", "Дата", "Статус"])
                analysis_table.setRowCount(len(analysis_results))
                
                for row, result in enumerate(analysis_results):
                    analysis_table.setItem(row, 0, QTableWidgetItem(result.get('analysis_name', '')))
                    analysis_table.setItem(row, 1, QTableWidgetItem(
                        result.get('result_date', '') if isinstance(result.get('result_date'), str) 
                        else result.get('result_date', '').strftime('%d.%m.%Y %H:%M')
                    ))
                    status_item = QTableWidgetItem(self.get_analysis_status(result.get('status', '')))
                    analysis_table.setItem(row, 2, status_item)
                
                analysis_table.resizeColumnsToContents()
                analysis_layout.addWidget(analysis_table)
                analysis_group.setLayout(analysis_layout)
                layout.addWidget(analysis_group)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        
        change_status_button = QPushButton("Изменить статус")
        change_status_button.clicked.connect(self.change_appointment_status)
        buttons_layout.addWidget(change_status_button)
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def get_status_text(self, status):
        """Возвращает текстовое представление статуса приема"""
        status_map = {
            'scheduled': 'Запланирован',
            'completed': 'Завершен',
            'cancelled': 'Отменен'
        }
        return status_map.get(status, status)
    
    def get_analysis_status(self, status):
        """Возвращает текстовое представление статуса анализа"""
        status_map = {
            'pending': 'В обработке',
            'completed': 'Выполнен',
            'sent': 'Отправлен'
        }
        return status_map.get(status, status)
    
    def change_appointment_status(self):
        """Изменение статуса приема"""
        appointment_id = self.appointment_data.get('id')
        current_status = self.appointment_data.get('status')
        
        # Варианты статусов
        if current_status == 'scheduled':
            new_status = 'completed'
            status_text = 'Завершен'
        elif current_status == 'completed':
            new_status = 'scheduled'
            status_text = 'Запланирован'
        else:
            new_status = 'scheduled'
            status_text = 'Запланирован'
        
        reply = QMessageBox.question(
            self,
            "Изменение статуса",
            f"Изменить статус приема на '{status_text}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if db.update_appointment_status(appointment_id, new_status):
                QMessageBox.information(self, "Успех", "Статус приема успешно изменен")
                self.appointment_data['status'] = new_status
                self.accept()  # Закрываем окно
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось изменить статус приема")


class AnalysisDetailsDialog(QDialog):
    """Диалоговое окно с деталями анализа"""
    
    def __init__(self, analysis_data, parent=None):
        super().__init__(parent)
        self.analysis_data = analysis_data
        
        self.setWindowTitle(f"Детали анализа: {analysis_data.get('analysis_name', '')}")
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout()
        
        # Информация о пациенте и анализе
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_frame.setStyleSheet("background-color: #f0f0f0; padding: 10px;")
        info_layout = QFormLayout(info_frame)
        
        patient_name = QLabel(self.analysis_data.get('patient_name', ''))
        patient_name.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout.addRow("Пациент:", patient_name)
        
        info_layout.addRow("Тип анализа:", QLabel(self.analysis_data.get('analysis_name', '')))
        
        date_str = self.analysis_data.get('result_date', '')
        if not isinstance(date_str, str):
            date_str = date_str.strftime('%d.%m.%Y %H:%M')
        info_layout.addRow("Дата:", QLabel(date_str))
        
        status_text = {
            'pending': 'В обработке',
            'completed': 'Выполнен',
            'sent': 'Отправлен'
        }.get(self.analysis_data.get('status', ''), self.analysis_data.get('status', ''))
        
        info_layout.addRow("Статус:", QLabel(status_text))
        
        layout.addWidget(info_frame)
        
        # Результаты анализа
        results_group = QGroupBox("Результаты анализа")
        results_layout = QVBoxLayout()
        
        # Парсинг данных результата
        result_data = self.analysis_data.get('result_data', '{}')
        if isinstance(result_data, str):
            try:
                result_data = json.loads(result_data)
            except json.JSONDecodeError:
                result_data = {"Результат": result_data}
        
        # Отображение результатов в таблице
        if isinstance(result_data, dict) and result_data:
            results_table = QTableWidget()
            results_table.setColumnCount(3)
            results_table.setHorizontalHeaderLabels(["Параметр", "Значение", "Норма"])
            results_table.setRowCount(len(result_data))
            
            for row, (param, value) in enumerate(result_data.items()):
                results_table.setItem(row, 0, QTableWidgetItem(param))
                results_table.setItem(row, 1, QTableWidgetItem(str(value)))
                
                # Нормальные значения по справочнику (добавить при необходимости)
                normal_value = self.get_normal_value(param)
                normal_item = QTableWidgetItem(normal_value)
                results_table.setItem(row, 2, normal_item)
            
            results_table.resizeColumnsToContents()
            results_layout.addWidget(results_table)
        else:
            results_layout.addWidget(QLabel("Нет данных о результатах анализа"))
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
    
    def get_normal_value(self, parameter):
        """Получение нормальных значений для параметра анализа"""
        normal_values = {
            'Гемоглобин': '120-160 г/л',
            'Эритроциты': '3.8-5.5 млн/мкл',
            'Лейкоциты': '4.0-9.0 тыс/мкл',
            'Тромбоциты': '180-320 тыс/мкл',
            'СОЭ': '2-15 мм/ч',
            'Глюкоза': '3.9-6.1 ммоль/л',
            'Холестерин': '3.0-5.2 ммоль/л',
            'Билирубин': '3.4-17.1 мкмоль/л',
            'АЛТ': '5-40 ед/л',
            'АСТ': '5-40 ед/л',
            'Креатинин': '53-106 мкмоль/л',
            'Мочевина': '2.5-8.3 ммоль/л',
            'pH': '5.0-7.0',
            'Белок': 'Отсутствует',
            'Кетоновые тела': 'Отсутствуют',
            'Цвет': 'Светло-желтый',
            'Прозрачность': 'Прозрачная'
        }
        return normal_values.get(parameter, 'Не определено')


class DoctorWindow(QMainWindow):
    """Главное окно интерфейса врача"""
    logout_signal = Signal()
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        
        # Получаем информацию о враче
        self.doctor_info = db.get_doctor_by_user_id(user_data['id'])
        
        self.setWindowTitle(f"Медицинский центр - Врач: {user_data['full_name']}")
        self.setMinimumSize(800, 600)
        
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
        
        user_info = QLabel(f"Врач: {self.user_data['full_name']}")
        user_info.setStyleSheet("font-weight: bold;")
        top_panel.addWidget(user_info)
        
        if self.doctor_info:
            specialization = QLabel(f"Специализация: {self.doctor_info['specialization']}")
            top_panel.addWidget(specialization)
        
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
        
        # Вкладка расписания
        self.schedule_tab = QWidget()
        self.setup_schedule_tab()
        self.tab_widget.addTab(self.schedule_tab, "Расписание")
        
        # Вкладка анализов
        self.analysis_tab = QWidget()
        self.setup_analysis_tab()
        self.tab_widget.addTab(self.analysis_tab, "Анализы")
        
        main_layout.addWidget(self.tab_widget)
    
    def setup_schedule_tab(self):
        """Настройка вкладки расписания"""
        layout = QVBoxLayout(self.schedule_tab)
        
        # Верхняя панель с фильтрами
        filter_layout = QHBoxLayout()
        
        date_label = QLabel("Дата:")
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setCalendarPopup(True)
        
        apply_filter_button = QPushButton("Применить")
        apply_filter_button.clicked.connect(self.load_schedule)
        
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.date_filter)
        filter_layout.addWidget(apply_filter_button)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Таблица с расписанием
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels([
            "Дата", "Время", "Пациент", "Статус", "Примечания", "Действия"
        ])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.setSortingEnabled(True)
        
        layout.addWidget(self.schedule_table)
        
        # Загрузка расписания
        self.load_schedule()
    
    def setup_analysis_tab(self):
        """Настройка вкладки анализов"""
        layout = QVBoxLayout(self.analysis_tab)
        
        # Верхняя панель с фильтрами
        filter_layout = QHBoxLayout()
        
        patient_label = QLabel("Пациент:")
        self.patient_filter = QComboBox()
        self.patient_filter.addItem("Все пациенты", None)
        
        # Загрузка списка пациентов
        patients = db.get_all_patients()
        for patient in patients:
            self.patient_filter.addItem(patient['full_name'], patient['id'])
        
        date_label = QLabel("Период:")
        self.start_date_filter = QDateEdit()
        self.start_date_filter.setDate(QDate.currentDate().addDays(-30))
        self.start_date_filter.setCalendarPopup(True)
        
        date_to_label = QLabel("по")
        
        self.end_date_filter = QDateEdit()
        self.end_date_filter.setDate(QDate.currentDate())
        self.end_date_filter.setCalendarPopup(True)
        
        apply_filter_button = QPushButton("Применить")
        apply_filter_button.clicked.connect(self.load_analysis_results)
        
        filter_layout.addWidget(patient_label)
        filter_layout.addWidget(self.patient_filter)
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.start_date_filter)
        filter_layout.addWidget(date_to_label)
        filter_layout.addWidget(self.end_date_filter)
        filter_layout.addWidget(apply_filter_button)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Таблица с результатами анализов
        self.analysis_table = QTableWidget()
        self.analysis_table.setColumnCount(6)
        self.analysis_table.setHorizontalHeaderLabels([
            "Дата", "Пациент", "Тип анализа", "Статус", "Лаборант", "Действия"
        ])
        self.analysis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.analysis_table.setSortingEnabled(True)
        
        layout.addWidget(self.analysis_table)
        
        # Загрузка результатов анализов
        self.load_analysis_results()
    
    def load_schedule(self):
        """Загрузка расписания врача"""
        if not self.doctor_info:
            QMessageBox.warning(self, "Предупреждение", "Нет информации о враче. Пожалуйста, обратитесь к администратору.")
            return
        
        # Получение даты из фильтра
        filter_date = self.date_filter.date().toString("yyyy-MM-dd")
        
        print(f"Загрузка расписания для врача ID: {self.doctor_info['id']} на дату: {filter_date}")
        
        # Получение расписания из базы данных
        try:
            appointments = db.fetch_all("""
                SELECT a.*, p.full_name as patient_name 
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                WHERE a.doctor_id = ?
                ORDER BY a.appointment_date
            """, (self.doctor_info['id'],))
            
            print(f"Найдено записей: {len(appointments)}")
            
            # Фильтрация по дате на стороне приложения
            filtered_appointments = []
            for appointment in appointments:
                appointment_date = appointment['appointment_date'].split()[0]  # Получаем только дату без времени
                if appointment_date == filter_date:
                    filtered_appointments.append(appointment)
            
            print(f"После фильтрации осталось записей: {len(filtered_appointments)}")
            
            # Заполнение таблицы
            self.schedule_table.setRowCount(len(filtered_appointments))
            
            for row, appointment in enumerate(filtered_appointments):
                # Время
                appointment_datetime = appointment['appointment_date']
                try:
                    if isinstance(appointment_datetime, str):
                        date_time = datetime.strptime(appointment_datetime, "%Y-%m-%d %H:%M:%S")
                        time_item = QTableWidgetItem(date_time.strftime("%H:%M"))
                    else:
                        time_item = QTableWidgetItem(appointment_datetime.strftime("%H:%M"))
                except Exception as e:
                    print(f"Ошибка обработки даты: {e}")
                    time_item = QTableWidgetItem(str(appointment_datetime))
                
                self.schedule_table.setItem(row, 0, time_item)
                
                # Пациент
                patient_item = QTableWidgetItem(appointment['patient_name'])
                self.schedule_table.setItem(row, 1, patient_item)
                
                # Примечания
                notes_item = QTableWidgetItem(appointment['notes'] if appointment['notes'] else "")
                self.schedule_table.setItem(row, 2, notes_item)
                
                # Статус
                status_text = {
                    'scheduled': 'Запланирован',
                    'completed': 'Завершен',
                    'cancelled': 'Отменен'
                }.get(appointment['status'], appointment['status'])
                
                status_item = QTableWidgetItem(status_text)
                
                # Цветовое выделение статуса
                if appointment['status'] == 'scheduled':
                    status_item.setBackground(QColor("#ffc107"))  # Желтый
                elif appointment['status'] == 'completed':
                    status_item.setBackground(QColor("#28a745"))  # Зеленый
                elif appointment['status'] == 'cancelled':
                    status_item.setBackground(QColor("#dc3545"))  # Красный
                
                self.schedule_table.setItem(row, 3, status_item)
                
                # Кнопка действий
                view_button = QPushButton("Просмотр")
                view_button.clicked.connect(lambda checked, a=appointment: self.view_appointment_details(a))
                self.schedule_table.setCellWidget(row, 4, view_button)
        except Exception as e:
            print(f"Ошибка при загрузке расписания: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить расписание: {str(e)}")
        
        self.schedule_table.resizeColumnsToContents()
    
    def load_analysis_results(self):
        """Загрузка результатов анализов"""
        # Получение параметров фильтрации
        patient_id = self.patient_filter.currentData()
        start_date = self.start_date_filter.date().toString("yyyy-MM-dd")
        end_date = self.end_date_filter.date().toString("yyyy-MM-dd")
        
        print(f"Загрузка анализов за период: {start_date} - {end_date}, пациент ID: {patient_id}")
        
        try:
            # Базовый запрос без фильтра по дате (будем фильтровать на стороне приложения)
            query = """
                SELECT ar.*, at.name as analysis_name, p.full_name as patient_name, u.full_name as lab_technician_name 
                FROM analysis_results ar
                JOIN analysis_types at ON ar.analysis_type_id = at.id
                JOIN patients p ON ar.patient_id = p.id
                JOIN users u ON ar.lab_user_id = u.id
            """
            params = []
            
            # Добавление фильтра по пациенту, если выбран
            if patient_id:
                query += " WHERE ar.patient_id = ?"
                params.append(patient_id)
            
            query += " ORDER BY ar.result_date DESC"
            
            # Получение результатов анализов
            all_analysis_results = db.fetch_all(query, params)
            print(f"Найдено записей: {len(all_analysis_results)}")
            
            # Фильтрация по дате на стороне приложения
            filtered_results = []
            for result in all_analysis_results:
                try:
                    result_date_str = result['result_date']
                    if isinstance(result_date_str, str):
                        result_date = result_date_str.split()[0]  # Получаем только дату без времени
                    else:
                        result_date = result_date_str.strftime('%Y-%m-%d')
                    
                    if start_date <= result_date <= end_date:
                        filtered_results.append(result)
                except Exception as e:
                    print(f"Ошибка обработки даты для анализа: {e}")
                    # Включаем результат, если не можем определить дату
                    filtered_results.append(result)
            
            print(f"После фильтрации осталось записей: {len(filtered_results)}")
            
            # Заполнение таблицы
            self.analysis_table.setRowCount(len(filtered_results))
            
            for row, result in enumerate(filtered_results):
                # Пациент
                patient_item = QTableWidgetItem(result['patient_name'])
                self.analysis_table.setItem(row, 0, patient_item)
                
                # Тип анализа
                analysis_item = QTableWidgetItem(result['analysis_name'])
                self.analysis_table.setItem(row, 1, analysis_item)
                
                # Дата
                try:
                    date_str = result['result_date']
                    if isinstance(date_str, str):
                        # Если дата уже в строковом формате, пытаемся отформатировать её
                        try:
                            date_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                            date_item = QTableWidgetItem(date_time.strftime('%d.%m.%Y %H:%M'))
                        except:
                            date_item = QTableWidgetItem(date_str)
                    else:
                        # Если дата - объект datetime
                        date_item = QTableWidgetItem(date_str.strftime('%d.%m.%Y %H:%M'))
                except Exception as e:
                    print(f"Ошибка форматирования даты: {e}")
                    date_item = QTableWidgetItem(str(result.get('result_date', '')))
                
                self.analysis_table.setItem(row, 2, date_item)
                
                # Статус
                status_text = {
                    'pending': 'В обработке',
                    'completed': 'Выполнен',
                    'sent': 'Отправлен'
                }.get(result['status'], result['status'])
                
                status_item = QTableWidgetItem(status_text)
                self.analysis_table.setItem(row, 3, status_item)
                
                # Лаборант
                lab_technician_item = QTableWidgetItem(result['lab_technician_name'])
                self.analysis_table.setItem(row, 4, lab_technician_item)
                
                # Кнопка действий
                view_button = QPushButton("Просмотр")
                view_button.clicked.connect(lambda checked, r=result: self.view_analysis_details(r))
                self.analysis_table.setCellWidget(row, 5, view_button)
        except Exception as e:
            print(f"Ошибка при загрузке анализов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить результаты анализов: {str(e)}")
            
        self.analysis_table.resizeColumnsToContents()
    
    def view_appointment_details(self, appointment):
        """Просмотр деталей приема"""
        dialog = AppointmentDetailsDialog(appointment, self)
        result = dialog.exec()
        
        # Обновление таблицы после изменения статуса
        if result == QDialog.Accepted:
            self.load_schedule()
    
    def view_analysis_details(self, analysis):
        """Просмотр деталей анализа"""
        dialog = AnalysisDetailsDialog(analysis, self)
        dialog.exec()
    
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
        'id': 2,
        'username': 'doctor1',
        'full_name': 'Петров Иван Сергеевич',
        'role': 'doctor'
    }
    
    window = DoctorWindow(test_user)
    window.show()
    
    sys.exit(app.exec()) 