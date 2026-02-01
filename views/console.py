
"""Консоль сообщений"""

import tkinter as tk
from tkinter import scrolledtext

class ConsoleView:
    def __init__(self):
        self.create_widgets()
        
    def create_widgets(self):
        """Создание виджетов консоли"""
        self.frame = tk.LabelFrame(
            text="Консоль сообщений", 
            font=("Arial", 12, "bold"), 
            bg='white', 
            bd=2
        )
        
        self.text_box = scrolledtext.ScrolledText(
            self.frame, 
            height=15,
            font=("Consolas", 10),
            bg='white',
            fg='black',
            wrap=tk.WORD
        )
        self.text_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def log(self, text):
        """Добавление сообщения в лог"""
        self.text_box.insert(tk.END, text + "\n")
        self.text_box.see(tk.END)
        
    def clear(self):
        """Очистка консоли"""
        self.text_box.delete(1.0, tk.END)
        
    def get_text(self):
        """Получение текста из консоли"""
        return self.text_box.get(1.0, tk.END)