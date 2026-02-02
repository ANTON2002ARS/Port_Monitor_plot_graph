"""Виджет настроек сенсоров"""

import tkinter as tk
from tkinter import ttk
from config import BUTTON_STYLE, BAUDRATES, SENSOR_TAGS, DEFAULT_COLORS

class SensorSettingsView:
    def __init__(self, controller):
        self.controller = controller
        self.create_widgets()
        
    def create_widgets(self):
        """Создание виджетов настроек сенсоров"""
        self.frame = tk.LabelFrame(
            text="Настройки сенсоров",
            font=("Arial", 12, "bold"), 
            bg='white', 
            bd=2
        )
        
        self.sensor_widgets = {}
        
        for tag in SENSOR_TAGS:
            sensor_frame = tk.Frame(self.frame, bg='white')
            sensor_frame.pack(fill=tk.X, pady=5, padx=10)
            
            # Переменные
            port_var = tk.StringVar()
            baud_var = tk.IntVar(value=115200)
            use_var = tk.BooleanVar(value=False if tag in ["SENSOR_3", "SENSOR_4"] else True)
            save_var = tk.BooleanVar(value=True)  # Автосохранение включено по умолчанию
            
            # Чекбокс использования сенсора
            use_cb = tk.Checkbutton(
                sensor_frame, 
                text=tag, 
                variable=use_var,
                font=("Arial", 10, "bold"),
                bg='white'
            )
            use_cb.pack(side=tk.LEFT, padx=(0, 10))
            
            # Выбор порта
            tk.Label(sensor_frame, text="Порт:", bg='white').pack(side=tk.LEFT, padx=(0, 5))
            port_menu = tk.OptionMenu(sensor_frame, port_var, "")
            port_menu.pack(side=tk.LEFT, padx=(0, 10))
            port_menu.config(width=10, **{k: v for k, v in BUTTON_STYLE.items() if k != "font"})
            
            # Выбор скорости
            tk.Label(sensor_frame, text="Скорость:", bg='white').pack(side=tk.LEFT, padx=(0, 5))
            baud_menu = tk.OptionMenu(sensor_frame, baud_var, *BAUDRATES)
            baud_menu.pack(side=tk.LEFT, padx=(0, 10))
            baud_menu.config(width=10, **{k: v for k, v in BUTTON_STYLE.items() if k != "font"})
            
            # Кнопка выбора цвета с цветом текста как у графика
            default_color = DEFAULT_COLORS.get(tag, "purple")
            color_btn = tk.Button(
                sensor_frame, 
                text="Цвет", 
                command=lambda t=tag: self.controller.choose_color(t),
                fg=default_color,
                bg='white',
                font=("Arial", 10),
                bd=2,
                relief="raised",
                padx=5,
                pady=2
            )
            color_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # Кнопка сохранения
            save_btn = tk.Button(
                sensor_frame, 
                text="Сохранить", 
                command=lambda t=tag: self.controller.save_sensor_data(t),
                **BUTTON_STYLE
            )
            save_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # Галочка автосохранения
            save_cb = tk.Checkbutton(
                sensor_frame, 
                text="Автосохранение", 
                variable=save_var,
                bg='white'
            )
            save_cb.pack(side=tk.LEFT)
            
            # Сохраняем виджеты
            self.sensor_widgets[tag] = {
                'frame': sensor_frame,
                'port_var': port_var,
                'baud_var': baud_var,
                'use_var': use_var,
                'save_var': save_var,
                'port_menu': port_menu,
                'baud_menu': baud_menu,
                'color_btn': color_btn,
                'color': default_color
            }
            
    def get_sensor_settings(self, tag):
        """Получение настроек сенсора"""
        widgets = self.sensor_widgets.get(tag)
        if widgets:
            return {
                'port': widgets['port_var'].get(),
                'baudrate': widgets['baud_var'].get(),
                'use_sensor': widgets['use_var'].get(),
                'auto_save': widgets['save_var'].get(),
                'color': widgets['color']
            }
        return None
        
    def update_port_list(self, ports):
        """Обновление списка портов"""
        for tag, widgets in self.sensor_widgets.items():
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
        """Установка цвета для сенсора и обновление кнопки"""
        if tag in self.sensor_widgets:
            self.sensor_widgets[tag]['color'] = color
            # Обновляем цвет текста кнопки
            self.sensor_widgets[tag]['color_btn'].config(fg=color)
            
    def lock_sensors(self):
        """Блокировка настроек сенсоров"""
        for widgets in self.sensor_widgets.values():
            widgets['port_menu'].config(state="disabled")
            widgets['baud_menu'].config(state="disabled")
            
    def unlock_sensors(self):
        """Разблокировка настроек сенсоров"""
        for widgets in self.sensor_widgets.values():
            widgets['port_menu'].config(state="normal")
            widgets['baud_menu'].config(state="normal")