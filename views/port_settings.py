"""Виджет настроек портов"""

import tkinter as tk
from tkinter import ttk
from config import BUTTON_STYLE, BAUDRATES, PORT_TAGS, DEFAULT_COLORS

class PortSettingsView:
    def __init__(self, controller):
        self.controller = controller
        self.create_widgets()
        
    def create_widgets(self):
        """Создание виджетов настроек портов"""
        self.frame = tk.LabelFrame(
            text="Настройки портов", 
            font=("Arial", 12, "bold"), 
            bg='white', 
            bd=2
        )
        
        self.port_widgets = {}
        
        for tag in PORT_TAGS:
            port_frame = tk.Frame(self.frame, bg='white')
            port_frame.pack(fill=tk.X, pady=5, padx=10)
            
            # Переменные
            port_var = tk.StringVar()
            baud_var = tk.IntVar(value=115200)
            use_var = tk.BooleanVar(value=False if tag in ["PORT3", "PORT4"] else True)
            save_var = tk.BooleanVar(value=True)
            
            # Виджеты
            use_cb = tk.Checkbutton(
                port_frame, 
                text=tag, 
                variable=use_var,
                font=("Arial", 10, "bold"),
                bg='white'
            )
            use_cb.pack(side=tk.LEFT, padx=(0, 10))
            
            # Выбор порта
            tk.Label(port_frame, text="Порт:", bg='white').pack(side=tk.LEFT, padx=(0, 5))
            port_menu = tk.OptionMenu(port_frame, port_var, "")
            port_menu.pack(side=tk.LEFT, padx=(0, 10))
            port_menu.config(width=10, **{k: v for k, v in BUTTON_STYLE.items() if k != "font"})
            
            # Выбор скорости
            tk.Label(port_frame, text="Скорость:", bg='white').pack(side=tk.LEFT, padx=(0, 5))
            baud_menu = tk.OptionMenu(port_frame, baud_var, *BAUDRATES)
            baud_menu.pack(side=tk.LEFT, padx=(0, 10))
            baud_menu.config(width=10, **{k: v for k, v in BUTTON_STYLE.items() if k != "font"})
            
            # Кнопка выбора цвета
            color_btn = tk.Button(
                port_frame, 
                text="Цвет", 
                command=lambda t=tag: self.controller.choose_color(t),
                **BUTTON_STYLE
            )
            color_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # Кнопка сохранения
            save_btn = tk.Button(
                port_frame, 
                text="Сохранить", 
                command=lambda t=tag: self.controller.save_port_data(t),
                **BUTTON_STYLE
            )
            save_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # Галочка автосохранения
            save_cb = tk.Checkbutton(
                port_frame, 
                text="Автосохранение", 
                variable=save_var,
                bg='white'
            )
            save_cb.pack(side=tk.LEFT)
            
            # Сохраняем виджеты
            self.port_widgets[tag] = {
                'frame': port_frame,
                'port_var': port_var,
                'baud_var': baud_var,
                'use_var': use_var,
                'save_var': save_var,
                'port_menu': port_menu,
                'baud_menu': baud_menu,
                'color': DEFAULT_COLORS.get(tag, "purple")
            }
            
    def get_port_settings(self, tag):
        """Получение настроек порта"""
        widgets = self.port_widgets.get(tag)
        if widgets:
            return {
                'port': widgets['port_var'].get(),
                'baudrate': widgets['baud_var'].get(),
                'use_port': widgets['use_var'].get(),
                'auto_save': widgets['save_var'].get(),
                'color': widgets['color']
            }
        return None
        
    def update_port_list(self, ports):
        """Обновление списка портов"""
        for tag, widgets in self.port_widgets.items():
            current_value = widgets['port_var'].get()
            widgets['port_menu']['menu'].delete(0, "end")
            
            # Добавляем пустую строку
            widgets['port_menu']['menu'].add_command(
                label="", 
                command=tk._setit(widgets['port_var'], "")
            )
            
            for p in ports:
                widgets['port_menu']['menu'].add_command(
                    label=p, 
                    command=tk._setit(widgets['port_var'], p)
                )
            
            # Восстанавливаем предыдущее значение
            if current_value in ports:
                widgets['port_var'].set(current_value)
            else:
                widgets['port_var'].set("")
                
    def set_color(self, tag, color):
        """Установка цвета для порта"""
        if tag in self.port_widgets:
            self.port_widgets[tag]['color'] = color
            
    def lock_ports(self):
        """Блокировка настроек портов"""
        for widgets in self.port_widgets.values():
            widgets['port_menu'].config(state="disabled")
            widgets['baud_menu'].config(state="disabled")
            # Не блокируем чекбоксы, чтобы можно было отключать порты на лету
            
    def unlock_ports(self):
        """Разблокировка настроек портов"""
        for widgets in self.port_widgets.values():
            widgets['port_menu'].config(state="normal")
            widgets['baud_menu'].config(state="normal")