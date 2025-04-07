import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import json

class EmailSender:
    """Класс для отправки электронных писем с результатами анализов"""
    
    def __init__(self, smtp_server='smtp.mail.ru', port=587, username='', password=''):
        """Инициализация параметров подключения к SMTP серверу"""
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password
        
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
            
            # Установка соединения с SMTP-сервером и отправка письма
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.sendmail(self.username, recipient_email, message.as_string())
            
            return True
        
        except Exception as e:
            print(f"Ошибка при отправке email: {str(e)}")
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
email_sender = EmailSender()

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