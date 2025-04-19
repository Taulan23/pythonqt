#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для тестирования отправки email через SMTP
"""

from email_sender import EmailSender
import sys

def test_email_sending(recipient_email):
    """
    Тестирует отправку email по указанному адресу
    """
    # Создаем экземпляр EmailSender с вашими учетными данными
    # ВАЖНО: Замените значения username и password на ваши реальные данные
    email_sender = EmailSender(
        smtp_server='smtp.gmail.com',  # Для Gmail
        port=587,
        username='roma.hatuaev@gmail.com',  # Ваш Gmail
        password='javascript22',  # Ваш пароль приложения
        test_mode=False  # Включаем реальную отправку
    )
    
    # Формируем тестовые данные анализа
    result_data = {
        'Гемоглобин': '135 г/л',
        'Эритроциты': '4.5 млн/мкл',
        'Лейкоциты': '6.2 тыс/мкл',
        'Тромбоциты': '250 тыс/мкл',
        'СОЭ': '10 мм/ч'
    }
    
    print(f"Отправка тестового email на адрес: {recipient_email}")
    
    # Отправляем тестовое письмо
    success = email_sender.send_analysis_results(
        recipient_email=recipient_email,
        subject='Тестовое письмо из медицинского центра',
        patient_name='Тестовый Пациент',
        analysis_name='Общий анализ крови (тестовый)',
        result_data=result_data
    )
    
    if success:
        print("✅ Тест успешно выполнен! Письмо отправлено.")
        print(f"Проверьте входящие сообщения на адресе {recipient_email}")
    else:
        print("❌ Ошибка при отправке письма.")
        print("Убедитесь, что вы указали правильные данные SMTP в файле.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Если пользователь указал email аргументом
        recipient_email = sys.argv[1]
        test_email_sending(recipient_email)
    else:
        # Запрашиваем email у пользователя
        recipient_email = input("Введите email для отправки тестового письма: ")
        test_email_sending(recipient_email) 