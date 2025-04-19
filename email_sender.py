import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import json
from datetime import datetime, timedelta

class EmailSender:
    """Класс для отправки электронных писем с результатами анализов"""
    
    def __init__(self, smtp_server='smtp.gmail.com', port=587, username='', password='', test_mode=False):
        """Инициализация параметров подключения к SMTP серверу"""
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password
        self.test_mode = test_mode  # Режим тестирования без реальной отправки
        
        # Если учетные данные не указаны, пытаемся получить их из переменных окружения
        if not username:
            self.username = os.environ.get('MAIL_USERNAME', '')
        if not password:
            self.password = os.environ.get('MAIL_PASSWORD', '')
    
    def send_analysis_results(self, recipient_email, subject, patient_name, analysis_name, result_data, attachments=None):
        """
        Отправка результатов анализов по электронной почте
        
        :param recipient_email: Email получателя
        :param subject: Тема письма
        :param patient_name: Имя пациента
        :param analysis_name: Название анализа
        :param result_data: Данные результатов анализа (строка или словарь)
        :param attachments: Список путей к файлам для прикрепления
        :return: True в случае успеха, False в случае ошибки
        """
        try:
            # Создание объекта сообщения
            message = MIMEMultipart()
            message['From'] = self.username
            message['To'] = recipient_email
            message['Subject'] = subject
            
            # Преобразование данных результатов анализа в читаемый формат
            if isinstance(result_data, str):
                try:
                    result_data = json.loads(result_data)
                except json.JSONDecodeError:
                    # Если не удалось распарсить JSON, оставляем как строку
                    pass
            
            # Создание HTML-содержимого письма
            html_content = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                        .container {{ width: 80%; margin: 0 auto; padding: 20px; }}
                        h1 {{ color: #2c3e50; }}
                        h2 {{ color: #3498db; }}
                        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                        tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Результаты анализов</h1>
                        <p>Уважаемый(ая) <strong>{patient_name}</strong>,</p>
                        <p>Направляем Вам результаты анализа <strong>{analysis_name}</strong>.</p>
                        
                        <h2>Результаты:</h2>
                        <table>
                            <tr>
                                <th>Параметр</th>
                                <th>Значение</th>
                                <th>Нормальные значения</th>
                            </tr>
            """
            
            # Добавление результатов анализа в таблицу
            if isinstance(result_data, dict):
                for param, value in result_data.items():
                    # Здесь можно добавить нормальные значения для каждого параметра
                    normal_values = self._get_normal_values(param)
                    html_content += f"""
                    <tr>
                        <td>{param}</td>
                        <td>{value}</td>
                        <td>{normal_values}</td>
                    </tr>
                    """
            else:
                # Если результаты не в формате словаря, просто выводим их как текст
                html_content += f"""
                <tr>
                    <td colspan="3">{result_data}</td>
                </tr>
                """
            
            html_content += """
                        </table>
                        
                        <p>С уважением,<br>Медицинский центр</p>
                    </div>
                </body>
            </html>
            """
            
            # Прикрепление HTML-содержимого к письму
            message.attach(MIMEText(html_content, 'html'))
            
            # Прикрепление файлов, если они указаны
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        with open(file_path, 'rb') as file:
                            part = MIMEApplication(file.read(), Name=os.path.basename(file_path))
                            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                            message.attach(part)
            
            # В тестовом режиме не отправляем письмо, а только выводим информацию
            if self.test_mode:
                print(f"\n[ТЕСТОВЫЙ РЕЖИМ] Отправка email:")
                print(f"От: {self.username}")
                print(f"Кому: {recipient_email}")
                print(f"Тема: {subject}")
                print(f"Содержание: HTML-письмо с результатами анализа {analysis_name}")
                if attachments:
                    print(f"Вложения: {', '.join([os.path.basename(f) for f in attachments if os.path.isfile(f)])}")
                print("Email успешно отправлен (тестовый режим)")
                return True
            
            # Установка соединения с SMTP-сервером и отправка письма (только если не тестовый режим)
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.sendmail(self.username, recipient_email, message.as_string())
            
            return True
        
        except Exception as e:
            print(f"Ошибка при отправке email: {str(e)}")
            return False
    
    def send_appointment_reminder(self, recipient_email, patient_name, doctor_name, appointment_date, appointment_time, doctor_specialization=None, notes=None):
        """
        Отправка напоминания о предстоящем приеме
        
        :param recipient_email: Email получателя (пациента)
        :param patient_name: Имя пациента
        :param doctor_name: Имя врача
        :param appointment_date: Дата приема (строка в формате YYYY-MM-DD)
        :param appointment_time: Время приема (строка в формате HH:MM)
        :param doctor_specialization: Специализация врача (опционально)
        :param notes: Дополнительные примечания (опционально)
        :return: True в случае успеха, False в случае ошибки
        """
        try:
            # Создание объекта сообщения
            message = MIMEMultipart()
            message['From'] = self.username
            message['To'] = recipient_email
            message['Subject'] = f"Напоминание о приеме {appointment_date}"
            
            # Форматирование специализации врача, если она указана
            doctor_spec_text = f", {doctor_specialization}" if doctor_specialization else ""
            
            # Создание HTML-содержимого письма
            html_content = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                        .container {{ width: 80%; margin: 0 auto; padding: 20px; }}
                        h1 {{ color: #2c3e50; }}
                        .appointment-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                        .appointment-info h2 {{ color: #3498db; margin-top: 0; }}
                        .important {{ color: #e74c3c; font-weight: bold; }}
                        .notes {{ background-color: #fffde7; padding: 10px; border-left: 4px solid #ffd600; margin-top: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Напоминание о приеме</h1>
                        <p>Уважаемый(ая) <strong>{patient_name}</strong>,</p>
                        <p>Напоминаем Вам о предстоящем приеме в нашем медицинском центре.</p>
                        
                        <div class="appointment-info">
                            <h2>Информация о приеме:</h2>
                            <p><strong>Дата:</strong> {appointment_date}</p>
                            <p><strong>Время:</strong> {appointment_time}</p>
                            <p><strong>Врач:</strong> {doctor_name}{doctor_spec_text}</p>
                        </div>
                        
                        <p class="important">Пожалуйста, не забудьте взять с собой паспорт и полис ОМС.</p>
            """
            
            # Добавление примечаний, если они указаны
            if notes:
                html_content += f"""
                        <div class="notes">
                            <p><strong>Дополнительная информация:</strong></p>
                            <p>{notes}</p>
                        </div>
                """
            
            html_content += """
                        <p>В случае невозможности посещения в указанное время, пожалуйста, свяжитесь с нами заранее.</p>
                        <p>С уважением,<br>Медицинский центр</p>
                    </div>
                </body>
            </html>
            """
            
            # Прикрепление HTML-содержимого к письму
            message.attach(MIMEText(html_content, 'html'))
            
            # В тестовом режиме не отправляем письмо, а только выводим информацию
            if self.test_mode:
                print(f"\n[ТЕСТОВЫЙ РЕЖИМ] Отправка email с напоминанием:")
                print(f"От: {self.username}")
                print(f"Кому: {recipient_email}")
                print(f"Тема: Напоминание о приеме {appointment_date}")
                print(f"Содержание: HTML-письмо с напоминанием о приеме к врачу {doctor_name}")
                print("Email успешно отправлен (тестовый режим)")
                return True
            
            # Установка соединения с SMTP-сервером и отправка письма
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.sendmail(self.username, recipient_email, message.as_string())
            
            return True
        
        except Exception as e:
            print(f"Ошибка при отправке напоминания: {str(e)}")
            return False
    
    def send_report(self, recipient_email, recipient_name, report_type, report_period, report_file_path, additional_text=None):
        """
        Отправка отчета по электронной почте сотруднику
        
        :param recipient_email: Email получателя (сотрудника)
        :param recipient_name: Имя получателя (сотрудника)
        :param report_type: Тип отчета (например, "Список пациентов", "Статистика приемов")
        :param report_period: Период отчета (например, "Март 2025", "1 кв. 2025")
        :param report_file_path: Путь к файлу отчета для прикрепления
        :param additional_text: Дополнительный текст для включения в письмо
        :return: True в случае успеха, False в случае ошибки
        """
        try:
            # Проверка существования файла отчета
            if not os.path.isfile(report_file_path):
                print(f"Ошибка: файл отчета {report_file_path} не найден")
                return False
            
            # Создание объекта сообщения
            message = MIMEMultipart()
            message['From'] = self.username
            message['To'] = recipient_email
            message['Subject'] = f"Отчет: {report_type} за {report_period}"
            
            # Создание HTML-содержимого письма
            html_content = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                        .container {{ width: 80%; margin: 0 auto; padding: 20px; }}
                        h1 {{ color: #2c3e50; }}
                        .report-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                        .additional-info {{ background-color: #e8f4fe; padding: 10px; border-left: 4px solid #2196f3; margin-top: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Отчет: {report_type}</h1>
                        <p>Уважаемый(ая) <strong>{recipient_name}</strong>,</p>
                        <p>Направляем Вам отчет <strong>"{report_type}"</strong> за период <strong>{report_period}</strong>.</p>
                        
                        <div class="report-info">
                            <p>Файл отчета прикреплен к письму.</p>
                            <p>Тип файла: {os.path.splitext(report_file_path)[1]}</p>
                        </div>
            """
            
            # Добавление дополнительной информации, если она указана
            if additional_text:
                html_content += f"""
                        <div class="additional-info">
                            <p><strong>Дополнительная информация:</strong></p>
                            <p>{additional_text}</p>
                        </div>
                """
            
            html_content += """
                        <p>С уважением,<br>Медицинский центр</p>
                    </div>
                </body>
            </html>
            """
            
            # Прикрепление HTML-содержимого к письму
            message.attach(MIMEText(html_content, 'html'))
            
            # Прикрепление файла отчета
            with open(report_file_path, 'rb') as file:
                part = MIMEApplication(file.read(), Name=os.path.basename(report_file_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_file_path)}"'
                message.attach(part)
            
            # В тестовом режиме не отправляем письмо, а только выводим информацию
            if self.test_mode:
                print(f"\n[ТЕСТОВЫЙ РЕЖИМ] Отправка отчета:")
                print(f"От: {self.username}")
                print(f"Кому: {recipient_email}")
                print(f"Тема: Отчет: {report_type} за {report_period}")
                print(f"Содержание: HTML-письмо с отчетом")
                print(f"Вложение: {os.path.basename(report_file_path)}")
                print("Email успешно отправлен (тестовый режим)")
                return True
            
            # Установка соединения с SMTP-сервером и отправка письма
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.sendmail(self.username, recipient_email, message.as_string())
            
            return True
        
        except Exception as e:
            print(f"Ошибка при отправке отчета: {str(e)}")
            return False
    
    def _get_normal_values(self, parameter):
        """
        Получение нормальных значений для параметра анализа
        В реальном приложении эти данные могли бы храниться в базе данных
        
        :param parameter: Имя параметра анализа
        :return: Строка с нормальными значениями
        """
        # Словарь с нормальными значениями для некоторых параметров
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
            'Кетоновые тела': 'Отсутствуют'
        }
        
        return normal_values.get(parameter, 'Не указано')


# Создание экземпляра для использования в других модулях
email_sender = EmailSender(test_mode=False)  # Включаем реальную отправку

# ИНСТРУКЦИЯ ПО НАСТРОЙКЕ:
# 1. Для использования Gmail:
#    - Укажите свой Gmail адрес в параметре username
#    - Для password нужно создать пароль приложения:
#      а) Перейдите в настройки аккаунта Google -> Безопасность
#      б) Включите двухэтапную аутентификацию
#      в) Перейдите в раздел "Пароли приложений"
#      г) Создайте новый пароль приложения для "Другое (указать название)"
#      д) Используйте полученный пароль в параметре password
#
# 2. Пример использования с Gmail:
#    email_sender = EmailSender(
#        smtp_server='smtp.gmail.com',
#        port=587,
#        username='your_email@gmail.com',
#        password='your_app_password',
#        test_mode=False
#    )
#
# 3. Для использования Mail.ru:
#    - SMTP сервер: smtp.mail.ru
#    - Порт: 587
#    - Требуется включить SMTP в настройках почты Mail.ru
#
# 4. Для использования Yandex:
#    - SMTP сервер: smtp.yandex.ru
#    - Порт: 587
#    - Требуется включить SMTP в настройках почты Яндекс

# Пример использования:
"""
# Настройка учетных данных SMTP
email_sender = EmailSender(username='your_email@example.com', password='your_password')

# Данные анализа
result_data = {
    'Гемоглобин': '135 г/л',
    'Эритроциты': '4.5 млн/мкл',
    'Лейкоциты': '6.2 тыс/мкл',
    'Тромбоциты': '250 тыс/мкл',
    'СОЭ': '10 мм/ч'
}

# Отправка письма
success = email_sender.send_analysis_results(
    recipient_email='patient@example.com',
    subject='Результаты общего анализа крови',
    patient_name='Иванов Иван Иванович',
    analysis_name='Общий анализ крови',
    result_data=result_data
)

if success:
    print("Письмо успешно отправлено")
else:
    print("Произошла ошибка при отправке письма")
""" 