"""Главный контроллер приложения - теперь использует подконтроллеры"""

import tkinter as tk
import matplotlib.pyplot as plt
from config import SENSOR_TAGS

from controllers.base_controller import BaseController
from controllers.monitoring_controller import MonitoringController
from controllers.plot_controller import PlotController
from controllers.file_controller import FileController
from utils.plot_manager import PlotManager

class AppController(BaseController):
    """Главный контроллер, координирующий работу всех подконтроллеров"""
    
    def __init__(self):
        super().__init__()
        
        # Инициализируем подконтроллеры
        self.monitoring_controller = MonitoringController(self)
        self.plot_controller = PlotController(self)
        self.file_controller = FileController(self)
        
        # Специфичные атрибуты
        self.last_values = {tag: None for tag in self.SENSOR_TAGS}
        self.last_update_time = 0
        self.update_interval = 0.1
        
    def init_views(self, main_window, sensor_settings, adc_settings, control_panel, console):
        """Инициализация представлений"""
        super().init_views(main_window, sensor_settings, adc_settings, control_panel, console)
        
        # Инициализация менеджера графиков
        self.plot_manager = PlotManager(
            self.main_window.fig, 
            self.main_window.ax, 
            self.main_window.canvas,
            self.adc_params
        )
        
        # Настройка обработчиков
        self.main_window.on_closing(self.on_closing)
        
    # Методы, делегирующие работу подконтроллерам
    
    def start_monitoring(self):
        """Запуск мониторинга"""
        self.monitoring_controller.start_monitoring()
        
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring_controller.stop_monitoring()
        
    def read_com_port(self, port, baud, tag):
        """Чтение данных с COM порта"""
        self.monitoring_controller.read_com_port(port, baud, tag)
        
    def print_combined_values(self):
        """Вывод значений всех активных сенсоров в одну строку"""
        self.monitoring_controller.print_combined_values()
        
    def update_plot(self):
        """Обновление графика"""
        self.plot_controller.update_plot()
        
    def draw_loaded_graph(self):
        """Отрисовка графика загруженных данных"""
        self.plot_controller.draw_loaded_graph()
        
    def choose_color(self, tag):
        """Выбор цвета для сенсора"""
        self.plot_controller.choose_color(tag)
        
    def on_adc_settings_changed(self):
        """Обработчик изменения настроек АЦП"""
        self.plot_controller.on_adc_settings_changed()
        
    def load_graph(self):
        """Загрузка данных из файла"""
        self.plot_controller.load_graph()
        
    def clear_graph(self):
        """Очистка графика"""
        self.plot_controller.clear_graph()
        
    def toggle_display_mode(self):
        """Переключение режима отображения графика"""
        self.plot_controller.toggle_display_mode()
        
    def refresh_ports(self):
        """Обновление списка портов"""
        self.file_controller.refresh_ports()
        
    def copy_log(self):
        """Копирование лога в буфер обмена"""
        self.file_controller.copy_log()
        
    def save_sensor_data(self, tag):
        """Сохранение данных сенсора"""
        self.file_controller.save_sensor_data(tag)
        
    def show_about(self):
        """Показать информацию о программе"""
        self.file_controller.show_about()