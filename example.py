#!/usr/bin/env python3

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel

class SimpleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Создаем вертикальное расположение
        layout = QVBoxLayout()
        
        # Добавляем метку с текстом
        label = QLabel("Привет! Это тестовое приложение PyQt6")
        layout.addWidget(label)
        
        # Создаем кнопку
        btn = QPushButton("Нажми меня", self)
        btn.clicked.connect(self.on_button_click)
        layout.addWidget(btn)
        
        # Устанавливаем расположение для окна
        self.setLayout(layout)
        
        # Устанавливаем размер и заголовок окна
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle("PyQt6 Пример")
        self.show()
        
    def on_button_click(self):
        sender = self.sender()
        sender.setText("Кнопка была нажата!")

def main():
    app = QApplication(sys.argv)
    window = SimpleWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 