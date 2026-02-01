"""Виджет настроек АЦП"""

import tkinter as tk
from tkinter import ttk
from config import BUTTON_STYLE, ADC_BITS_OPTIONS, REF_VOLTAGE_OPTIONS

class ADCSettingsView:
    def __init__(self, controller):
        self.controller = controller
        self.create_widgets()
        self.setup_bindings()
        
    def create_widgets(self):
        """Создание виджетов настроек АЦП"""
        self.frame = tk.LabelFrame(
            text="ПАРАМЕТРЫ АЦП", 
            font=("Arial", 12, "bold"), 
            bg='white', 
            bd=2
        )
        
        inner_frame = tk.Frame(self.frame, bg='white')
        inner_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Настройка битности АЦП
        bits_frame = tk.Frame(inner_frame, bg='white')
        bits_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(bits_frame, text="Битность АЦП:", bg='white', width=15, anchor='w').pack(side=tk.LEFT)
        self.bits_var = tk.IntVar(value=10)
        self.bits_menu = tk.OptionMenu(bits_frame, self.bits_var, *ADC_BITS_OPTIONS)
        self.bits_menu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.bits_menu.config(width=12, **{k: v for k, v in BUTTON_STYLE.items() if k != "font"})
        
        # Настройка опорного напряжения
        voltage_frame = tk.Frame(inner_frame, bg='white')
        voltage_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(voltage_frame, text="Опорное напряжение:", bg='white', width=15, anchor='w').pack(side=tk.LEFT)
        self.voltage_var = tk.DoubleVar(value=5.0)
        self.voltage_menu = tk.OptionMenu(voltage_frame, self.voltage_var, *REF_VOLTAGE_OPTIONS)
        self.voltage_menu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.voltage_menu.config(width=12, **{k: v for k, v in BUTTON_STYLE.items() if k != "font"})
        
        # Информация
        info_frame = tk.Frame(inner_frame, bg='white')
        info_frame.pack(fill=tk.X, pady=(10, 5))
        
        tk.Label(info_frame, text="Текущие параметры:", font=("Arial", 10, "bold"), bg='white').pack(anchor='w')
        self.range_label = tk.Label(info_frame, text="Диапазон: 0-1024", bg='white')
        self.range_label.pack(anchor='w')
        self.voltage_label = tk.Label(info_frame, text="Напряжение: 0-5.0В", bg='white')
        self.voltage_label.pack(anchor='w')
        
    def setup_bindings(self):
        """Настройка привязок событий"""
        self.bits_var.trace('w', self.on_settings_changed)
        self.voltage_var.trace('w', self.on_settings_changed)
        
    def on_settings_changed(self, *args):
        """Обработчик изменения настроек"""
        self.controller.on_adc_settings_changed()
        self.update_info()
        
    def update_info(self):
        """Обновление информационных меток"""
        bits = self.bits_var.get()
        voltage = self.voltage_var.get()
        max_value = 2 ** bits
        
        self.range_label.config(text=f"Диапазон: 0-{max_value}")
        self.voltage_label.config(text=f"Напряжение: 0-{voltage}В")
        
    def lock_settings(self):
        """Блокировка настроек"""
        self.bits_menu.config(state="disabled")
        self.voltage_menu.config(state="disabled")
        
    def unlock_settings(self):
        """Разблокировка настроек"""
        self.bits_menu.config(state="normal")
        self.voltage_menu.config(state="normal")
        
    @property
    def bits(self):
        return self.bits_var.get()
        
    @property
    def ref_voltage(self):
        return self.voltage_var.get()