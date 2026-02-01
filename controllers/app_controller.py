"""Главный контроллер приложения"""

import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
import threading
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import atexit
import csv

from config import PORT_TAGS
from models.adc_parameters import ADCParameters
from models.data_buffer import DataBuffer
from utils.plot_manager import PlotManager
from utils.file_manager import FileManager
from utils.logger import Logger

class AppController:
    def __init__(self):
        self.program_running = False
        self.stop_threads_flag = False
        self.serial_ports = {}
        self.threads = {}
        self.active_ports = set()
        
        # Модели
        self.adc_params = ADCParameters()
        self.data_buffers = {tag: DataBuffer() for tag in PORT_TAGS}
        self.colors = {}
        
        # Утилиты
        self.plot_manager = None
        self.file_manager = FileManager()
        self.logger = Logger()
        
    def init_views(self, main_window, port_settings, adc_settings, control_panel, console):
        """Инициализация представлений"""
        self.main_window = main_window
        self.port_settings = port_settings
        self.adc_settings = adc_settings
        self.control_panel = control_panel
        self.console = console
        
        # Инициализация менеджера графиков
        self.plot_manager = PlotManager(
            self.main_window.fig, 
            self.main_window.ax, 
            self.main_window.canvas,
            self.adc_params
        )
        
        # Настройка обработчиков
        self.main_window.on_closing(self.on_closing)
        
    def start_monitoring(self):
        """Запуск мониторинга"""
        if self.program_running:
            return
            
        # Проверяем выбранные порты
        selected_ports = []
        for tag in PORT_TAGS:
            settings = self.port_settings.get_port_settings(tag)
            if settings and settings['use_port'] and settings['port']:
                selected_ports.append(tag)
                
        if not selected_ports:
            messagebox.showerror("Ошибка", "Выберите хотя бы один COM порт")
            return
            
        # Очистка графиков и данных
        self.clear_graph()
        self.stop_threads_flag = False
        self.active_ports = set(selected_ports)
        
        # Инициализация буферов
        for tag in selected_ports:
            settings = self.port_settings.get_port_settings(tag)
            if settings:
                self.colors[tag] = settings['color']
                self.data_buffers[tag].clear()
                
        # Обновление параметров АЦП
        self.adc_params.bits = self.adc_settings.bits
        self.adc_params.ref_voltage = self.adc_settings.ref_voltage
        
        # Блокировка настроек
        self.port_settings.lock_ports()
        self.adc_settings.lock_settings()
        
        # Запуск потоков
        self.program_running = True
        
        for tag in selected_ports:
            settings = self.port_settings.get_port_settings(tag)
            if settings:
                thread = threading.Thread(
                    target=self.read_com_port,
                    args=(settings['port'], settings['baudrate'], tag),
                    daemon=True
                )
                thread.start()
                self.threads[tag] = thread
                
        # Обновление графика
        self.update_plot()
        
        # Логирование
        self.logger.log("="*50)
        self.logger.log("=== ЗАПУСК МОНИТОРИНГА АЦП ===")
        self.logger.log(f"Битность АЦП: {self.adc_params.bits} бит")
        self.logger.log(f"Опорное напряжение: {self.adc_params.ref_voltage}В")
        self.logger.log(f"Диапазон АЦП: 0-{self.adc_params.max_value}")
        self.logger.log(f"Активные порты: {', '.join(selected_ports)}")
        self.logger.log("="*50)
        
    def stop_monitoring(self):
        """Остановка мониторинга"""
        if not self.program_running:
            return
            
        self.program_running = False
        self.stop_threads_flag = True
        
        # Логирование
        self.logger.log("="*50)
        self.logger.log("=== ОСТАНОВКА МОНИТОРИНГА ===")
        
        # Ожидание завершения потоков
        for tag, thread in self.threads.items():
            if thread.is_alive():
                thread.join(timeout=2.0)
                
        # Закрытие портов
        for tag, ser in list(self.serial_ports.items()):
            try:
                if ser and ser.is_open:
                    ser.close()
                    self.logger.log(f"[INFO] Закрыт порт {tag}")
            except Exception as e:
                self.logger.log(f"[ERROR] Ошибка закрытия порта {tag}: {e}")
                
        self.serial_ports.clear()
        self.threads.clear()
        
        # Автосохранение
        saved_count = 0
        for tag in PORT_TAGS:
            settings = self.port_settings.get_port_settings(tag)
            if (settings and settings['auto_save'] and 
                tag in self.data_buffers and self.data_buffers[tag].count > 0):
                
                color = self.colors.get(tag, "blue")
                file_path = self.file_manager.save_data(
                    tag, 
                    self.data_buffers[tag].raw_data,
                    color,
                    ask_filename=False
                )
                if file_path:
                    saved_count += 1
                    
        if saved_count > 0:
            self.logger.log(f"=== Сохранено файлов: {saved_count} ===")
            
        # Разблокировка настроек
        self.port_settings.unlock_ports()
        self.adc_settings.unlock_settings()
        
        # Очистка активных портов
        self.active_ports.clear()
        
    def read_com_port(self, port, baud, tag):
        """Чтение данных с COM порта"""
        try:
            ser = serial.Serial(port, baud, timeout=0.2)
            self.serial_ports[tag] = ser
            self.logger.log(f"[INFO] {tag}: {port} @ {baud} - Ожидание данных АЦП...")
        except Exception as e:
            self.logger.log(f"[ERROR] {tag}: {port}: {e}")
            self.active_ports.discard(tag)
            return
            
        while not self.stop_threads_flag and self.program_running:
            try:
                line = ser.readline().decode("utf-8").strip()
                if not line:
                    continue
                    
                raw_value = self.parse_value(line)
                if raw_value is None:
                    continue
                    
                # Преобразование в напряжение
                voltage = self.adc_params.raw_to_voltage(raw_value)
                
                # Сохранение данных
                self.data_buffers[tag].add_point(raw_value, voltage)
                
                # Логирование
                if tag in self.active_ports and raw_value != 0:
                    self.logger.log(
                        f"{tag}: {int(raw_value)} ({voltage:.3f}В)"
                    )
                    
            except serial.SerialException as e:
                if "read failed" in str(e) or "closed" in str(e):
                    break
                else:
                    self.logger.log(f"[ERROR] {tag}: {e}")
                    break
            except Exception as e:
                self.logger.log(f"[ERROR] {tag}: {e}")
                break
                
        # Закрытие порта
        try:
            ser.close()
            self.serial_ports.pop(tag, None)
            self.active_ports.discard(tag)
        except Exception as e:
            self.logger.log(f"[ERROR] Ошибка закрытия порта {tag}: {e}")
            
    def parse_value(self, line):
        """Парсинг строки данных"""
        parts = line.replace(" ", "").split(",")
        if len(parts) != 2:
            return None
            
        try:
            raw_value = float(parts[1])
            max_adc = self.adc_params.max_value
            
            if raw_value < 0 or raw_value > max_adc:
                self.logger.log(f"[WARNING] Значение вне диапазона 0-{max_adc}: {raw_value}")
                return None
                
            return raw_value
        except:
            return None
            
    def update_plot(self):
        """Обновление графика"""
        if not self.program_running:
            return  # Не обновляем, если мониторинг не запущен
        
        try:
            # Подготовка данных
            plot_data = {}
            for tag, buffer in self.data_buffers.items():
                if buffer.count > 0: #and tag in self.active_ports:
                    plot_data[tag] = {
                        'data': buffer.get_voltage_view(),
                        'color': self.colors.get(tag, "blue")
                    }
                
            # Обновление графика
            self.plot_manager.update_plot(
                plot_data,
                f"ADC Monitor ({self.adc_params.bits} бит, {self.adc_params.ref_voltage}В)"
            )
        
            # Планирование следующего обновления
            if self.program_running:
                self.main_window.root.after(300, self.update_plot)
            
        except Exception as e:
            self.logger.log(f"[ERROR] Ошибка обновления графика: {e}")


    def draw_loaded_graph(self):
        """Отрисовка графика загруженных данных"""
        try:
            # Подготовка данных
            plot_data = {}
            for tag, buffer in self.data_buffers.items():
                if buffer.count > 0:  # Убираем проверку на active_ports
                    plot_data[tag] = {
                        'data': buffer.get_voltage_view(),
                        'color': self.colors.get(tag, "blue")
                    }
                
            # Обновление графика
            if plot_data:
                title = f"Загруженные данные ADC ({self.adc_params.bits} бит, {self.adc_params.ref_voltage}В)"
                self.plot_manager.update_plot(plot_data, title)
            
        except Exception as e:
            self.logger.log(f"[ERROR] Ошибка отрисовки графика: {e}")



    def choose_color(self, tag):
        """Выбор цвета для порта"""
        color = colorchooser.askcolor(title=f"Цвет линии {tag}")
        if color[1]:
            self.colors[tag] = color[1]
            self.port_settings.set_color(tag, color[1])
            if self.program_running:
                self.update_plot()
                
    def on_adc_settings_changed(self):
        """Обработчик изменения настроек АЦП"""
        self.adc_params.bits = self.adc_settings.bits
        self.adc_params.ref_voltage = self.adc_settings.ref_voltage
        
        # Обновление буферов напряжения
        for tag, buffer in self.data_buffers.items():
            if buffer.count > 0:
                # Пересчет напряжений для существующих данных
                voltage_data = [self.adc_params.raw_to_voltage(v) 
                              for v in buffer.raw_data]
                buffer.voltage_data = voltage_data
                
        self.update_plot()
        self.adc_settings.update_info()
        
    def load_graph(self):
        """Загрузка данных из файла"""
        if self.program_running:
            messagebox.showwarning("Внимание", "Невозможно загрузить график во время работы мониторинга!")
            return
        
        files = filedialog.askopenfilenames(filetypes=[("CSV", "*.csv")])
        if not files:
            return
        
        for file in files:
            name, raw_data, color = self.file_manager.load_data(file, self.adc_params)
            if raw_data:
                # Используем существующий буфер или создаем новый
                if name not in self.data_buffers:
                    self.data_buffers[name] = DataBuffer()
                else:
                    self.data_buffers[name].clear()
                
                for raw_value in raw_data:
                    voltage = self.adc_params.raw_to_voltage(raw_value)
                    self.data_buffers[name].add_point(raw_value, voltage)
                
                self.colors[name] = color
                self.logger.log(f"[INFO] Загружено {len(raw_data)} значений: {name}")
            
        # Отрисовываем загруженные данные
        self.draw_loaded_graph()

        
    def clear_graph(self):
        """Очистка графика"""
        if self.program_running:
            messagebox.showwarning("Внимание", "Невозможно очистить график во время работы мониторинга!")
            return
        
        for buffer in self.data_buffers.values():
            buffer.clear()
        
        self.colors.clear()  # Очищаем цвета
        self.plot_manager.clear_plot()
        self.logger.log("[INFO] График очищен")

        
    def refresh_ports(self):
        """Обновление списка портов"""
        if self.program_running:
            messagebox.showwarning("Внимание", "Невозможно обновить список портов во время работы мониторинга!")
            return
            
        ports = self.get_com_ports()
        self.port_settings.update_port_list(ports)
        self.logger.log(f"[INFO] Список портов обновлен. Доступно портов: {len(ports)}")
        
    def get_com_ports(self):
        """Получение списка COM портов"""
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return [p for p in ports if p != 'COM1']
        
    def copy_log(self):
        """Копирование лога в буфер обмена"""
        self.main_window.root.clipboard_clear()
        self.main_window.root.clipboard_append(self.console.get_text())
        self.logger.log("[INFO] Лог скопирован в буфер обмена")
        
    def show_about(self):
        """Показать информацию о программе"""
        about_text = f"""
        ADC Monitor
        
        Программа для мониторинга АЦП через COM порты.
        
        Текущие настройки:
        - Битность АЦП: {self.adc_params.bits} бит
        - Опорное напряжение: {self.adc_params.ref_voltage}В
        - Диапазон АЦП: 0-{self.adc_params.max_value}
        
        Данные:
        - В логе и сохранениях: сырые значения АЦП
        - На графике: напряжение (0-{self.adc_params.ref_voltage}В)
        
        Формула преобразования для графика:
        Напряжение(V) = (ADC_RAW / {self.adc_params.max_value}) * {self.adc_params.ref_voltage}
        
        Формат данных с порта:
        ADC,<значение от 0 до {self.adc_params.max_value}>
        
        Например: ADC,512
        """
        messagebox.showinfo("О программе", about_text)
        
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
            
    def cleanup_resources(self):
        """Очистка ресурсов"""
        self.stop_monitoring()
        plt.close('all')
        
    def save_port_data(self, tag):
        """Сохранение данных порта"""
        if tag in self.data_buffers and self.data_buffers[tag].count > 0:
            color = self.colors.get(tag, "blue")
            self.file_manager.save_data(tag, self.data_buffers[tag].raw_data, color)