"""Главное окно приложения"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MainWindow:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("МОНИТОР СЕНСОРОВ")
        self.root.geometry("900x850")
        self.root.configure(bg='white')
        
        # Установка минимального размера окна
        self.root.minsize(900, 800)
        
        # Создание графической области
        self.create_plot_area()
        
        # Основной контейнер для нижней части
        self.bottom_container = tk.Frame(self.root, bg='white')
        self.bottom_container.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0, 10))
        
    def create_plot_area(self):
        """Создание области для графика"""
        # Создаем фигуру с увеличенным соотношением сторон для лучшего горизонтального растяжения
        self.fig = plt.Figure(figsize=(10, 5), dpi=100)  # Ширина 10, высота 5
        self.ax = self.fig.add_subplot(111)
        
        # Настройка размеров шрифтов для осей
        self.ax.tick_params(axis='both', which='major', labelsize=9)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def setup_ui(self, sensor_settings_view, adc_settings_view, control_panel, console_view):
        """Настройка пользовательского интерфейса"""
        # Левая часть - настройки сенсоров и консоль
        left_frame = tk.Frame(self.bottom_container, bg='white')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Сенсоры
        sensor_settings_view.frame.pack(in_=left_frame, fill=tk.X, pady=(0, 10))
        
        # Консоль
        console_view.frame.pack(in_=left_frame, fill=tk.BOTH, expand=True)
        
        # Правая часть - управление и настройки АЦП
        right_frame = tk.Frame(self.bottom_container, bg='white')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Панель управления
        control_panel.frame.pack(in_=right_frame, fill=tk.X, pady=(0, 10))
        
        # Настройки АЦП
        adc_settings_view.frame.pack(in_=right_frame, fill=tk.X, pady=(10, 0))
        
    def start(self):
        """Запуск главного цикла"""
        self.root.mainloop()
        
    def on_closing(self, callback):
        """Установка обработчика закрытия окна"""
        self.root.protocol("WM_DELETE_WINDOW", callback)