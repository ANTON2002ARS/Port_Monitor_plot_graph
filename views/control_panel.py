"""Панель управления приложением"""

import tkinter as tk
from config import BUTTON_STYLE

class ControlPanel:
    def __init__(self, controller):
        self.controller = controller
        self.create_widgets()
        
    def create_widgets(self):
        """Создание виджетов панели управления"""
        self.frame = tk.LabelFrame(
            text="Управление", 
            font=("Arial", 12, "bold"), 
            bg='white', 
            bd=2
        )
        
        control_column = tk.Frame(self.frame, bg='white')
        control_column.pack()
        
        # Кнопки управления с комментариями о блокировках
        buttons = [
            ("НАЧАТЬ", self.controller.start_monitoring, "green", "white"),
            ("ЗАВЕРШИТЬ", self.controller.stop_monitoring, "red", "white"),
            ("ОТКРЫТЬ ГРАФИК", self.controller.load_graph, "white", "black"),  # Блокируется при мониторинге
            ("ОЧИСТИТЬ ГРАФИК", self.controller.clear_graph, "white", "black"),  # Блокируется при мониторинге
            ("КОПИРОВАТЬ ЛОГИ", self.controller.copy_log, "white", "black"),
            ("Обновить COM", self.controller.refresh_ports, "white", "black"),  # Блокируется при мониторинге
            ("ПЕРЕКЛЮЧИТЬ ГРАФИК", self.controller.toggle_display_mode, "blue", "white"),  # Блокируется при мониторинге
            ("ЧТО ЗА ПРОГА", self.controller.show_about, "purple", "white"),
        ]
        
        for text, command, bg_color, fg_color in buttons:
            btn = tk.Button(
                control_column, text=text, width=20, height=1,
                command=command, bg=bg_color, fg=fg_color,
                font=("Arial", 10), bd=2, relief="raised"
            )
            btn.pack(pady=5)