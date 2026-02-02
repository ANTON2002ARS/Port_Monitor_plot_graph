"""Базовый контроллер для общих функций"""

import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import serial.tools.list_ports

from config import SENSOR_TAGS
from models.adc_parameters import ADCParameters
from models.data_buffer import DataBuffer
from utils.logger import Logger

class BaseController:
    """Базовый класс с общими методами для всех контроллеров"""
    
    def __init__(self):
        self.program_running = False
        self.stop_threads_flag = False
        self.serial_ports = {}
        self.threads = {}
        self.active_sensors = set()
        self.SENSOR_TAGS = SENSOR_TAGS  # Добавлено
        
        # Модели
        self.adc_params = ADCParameters()
        self.data_buffers = {tag: DataBuffer() for tag in SENSOR_TAGS}
        self.colors = {}
        
        # Утилиты
        self.logger = Logger()
        
        # Вьюхи (будут установлены позже)
        self.main_window = None
        self.sensor_settings = None
        self.adc_settings = None
        self.control_panel = None
        self.console = None
        self.plot_manager = None
        
    def init_views(self, main_window, sensor_settings, adc_settings, control_panel, console):
        """Инициализация представлений"""
        self.main_window = main_window
        self.sensor_settings = sensor_settings
        self.adc_settings = adc_settings
        self.control_panel = control_panel
        self.console = console
        
    def get_com_ports(self):
        """Получение списка COM портов"""
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return [p for p in ports if p != 'COM1']
        
    def cleanup_resources(self):
        """Очистка ресурсов"""
        self.stop_monitoring()
        plt.close('all')
        
    def on_closing(self):
        """Обработчик закрытия окна"""
        if self.program_running:
            if messagebox.askokcancel("Выход", 
                                      "Программа работает! Вы действительно хотите выйти?\n" 
                                      "Все данные будут сохранены согласно настройкам автосохранения."):
                self.stop_monitoring()
                self.cleanup_resources()
                self.main_window.root.destroy()
        else:
            self.cleanup_resources()
            self.main_window.root.destroy()
            
    def stop_monitoring(self):
        """Остановка мониторинга (базовая реализация, будет переопределена)"""
        pass