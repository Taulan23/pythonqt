#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PySide6 Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Создаем центральный виджет и его макет
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Добавляем метку с текстом
        label = QLabel("Тестовое окно PySide6 успешно запущено!")
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label)
        
        # Устанавливаем центральный виджет
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 