"""Логгер для приложения"""

class Logger:
    def __init__(self):
        self.callback = None
        
    def set_callback(self, callback):
        """Установка callback для вывода логов"""
        self.callback = callback
        
    def log(self, text):
        """Добавление сообщения в лог"""
        if self.callback:
            self.callback(text)
        else:
            print(text)