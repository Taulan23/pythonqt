import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class EmailSender:
    def __init__(self, smtp_server=None, smtp_port=None, username=None, password=None):
        """
        Инициализация отправщика email
        
        Args:
            smtp_server (str): SMTP сервер
            smtp_port (int): Порт SMTP сервера
            username (str): Имя пользователя (email)
            password (str): Пароль
        """
        self.smtp_server = smtp_server or "smtp.example.com"
        self.smtp_port = smtp_port or 587
        self.username = username or "user@example.com"
        self.password = password or "password"
    
    def send_analysis_results(self, patient_email, patient_name, analysis_type, attachment_path):
        """
        Отправить результаты анализа по email
        
        Args:
            patient_email (str): Email пациента
            patient_name (str): ФИО пациента
            analysis_type (str): Тип анализа
            attachment_path (str): Путь к файлу с результатами
        
        Returns:
            bool: True, если отправка успешна, иначе False
        """
        if not patient_email:
            return False
        
        try:
            # Создаем сообщение
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = patient_email
            msg['Subject'] = f"Результаты анализа: {analysis_type}"
            
            # Текст сообщения
            body = f"""
            Уважаемый(ая) {patient_name}!
            
            Во вложении находятся результаты вашего анализа: {analysis_type}.
            
            С уважением,
            Медицинский центр
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Прикрепляем файл
            with open(attachment_path, 'rb') as file:
                attachment = MIMEApplication(file.read(), Name=os.path.basename(attachment_path))
                attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(attachment)
            
            # Отправляем сообщение
            try:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()  # Защищенное соединение
                server.login(self.username, self.password)
                server.send_message(msg)
                server.quit()
                return True
            except Exception as e:
                print(f"Ошибка отправки email: {e}")
                # В демонстрационной версии просто выводим, что было бы отправлено
                print(f"Отправка email: {patient_email}")
                print(f"Тема: {msg['Subject']}")
                print(f"Текст: {body}")
                print(f"Вложение: {attachment_path}")
                return False
        except Exception as e:
            print(f"Ошибка формирования email: {e}")
            return False 