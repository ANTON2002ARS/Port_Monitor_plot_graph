"""Контроллер для управления графиками"""

from tkinter import messagebox
import os
from utils.file_manager import FileManager
from models.data_buffer import DataBuffer

class PlotController:
    """Управление графиками и отображением данных"""
    
    def __init__(self, base_controller):
        self.base = base_controller
        self.show_voltage = True
        self.last_update_time = 0
        self.update_interval = 0.1
        self.file_manager = FileManager()
        self.update_scheduled = False  # Добавлен флаг для отслеживания запланированных обновлений
        
    def update_plot(self):
        """Обновление графика"""
        if not self.base.program_running:
            self.update_scheduled = False
            return
        
        try:
            # Подготовка данных
            plot_data = {}
            for tag, buffer in self.base.data_buffers.items():
                if buffer.count > 0 and tag in self.base.active_sensors:
                    if self.show_voltage:
                        data_for_plot = buffer.get_voltage_view()
                    else:
                        data_for_plot = buffer.get_raw_view()
                    
                    plot_data[tag] = {
                        'data': data_for_plot,
                        'color': self.base.colors.get(tag, "blue")
                    }
                
            # Обновление графика с соответствующим заголовком
            if self.show_voltage:
                title = f"ADC Monitor - Напряжение ({self.base.adc_params.bits} бит, {self.base.adc_params.ref_voltage}В)"
                y_label = "Напряжение, В"
            else:
                title = f"ADC Monitor - Дискретные значения ({self.base.adc_params.bits} бит)"
                y_label = "Дискретное значение"
            
            self.base.plot_manager.update_plot(plot_data, title)
            self.base.main_window.ax.set_ylabel(y_label)
            self.base.main_window.canvas.draw()
        
            # Планируем следующее обновление, если мониторинг еще работает
            if self.base.program_running:
                self.update_scheduled = True
                self.base.main_window.root.after(300, self.update_plot)
            else:
                self.update_scheduled = False
            
        except Exception as e:
            self.base.logger.log(f"[ERROR] Ошибка обновления графика: {e}")
            self.update_scheduled = False

    def draw_loaded_graph(self):
        """Отрисовка графика загруженных данных"""
        try:
            # Подготовка данных
            plot_data = {}
            for tag, buffer in self.base.data_buffers.items():
                if buffer.count > 0:
                    if self.show_voltage:
                        data_for_plot = buffer.get_voltage_view()
                    else:
                        data_for_plot = buffer.get_raw_view()
                    
                    plot_data[tag] = {
                        'data': data_for_plot,
                        'color': self.base.colors.get(tag, "blue")
                    }
                
            if plot_data:
                if self.show_voltage:
                    title = f"Загруженные данные - Напряжение ({self.base.adc_params.bits} бит, {self.base.adc_params.ref_voltage}В)"
                    y_label = "Напряжение, В"
                else:
                    title = f"Загруженные данные - Дискретные значения ({self.base.adc_params.bits} бит)"
                    y_label = "Дискретное значение"
                
                self.base.plot_manager.update_plot(plot_data, title)
                self.base.main_window.ax.set_ylabel(y_label)
                self.base.main_window.canvas.draw()
            
        except Exception as e:
            self.base.logger.log(f"[ERROR] Ошибка отрисовки графика: {e}")

    def choose_color(self, tag):
        """Выбор цвета для сенсора (теперь можно менять во время мониторинга)"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(title=f"Цвет линии {tag}")
        if color[1]:
            self.base.colors[tag] = color[1]
            self.base.sensor_settings.set_color(tag, color[1])
            # Обновляем график если есть данные
            if any(buffer.count > 0 for buffer in self.base.data_buffers.values()):
                if self.base.program_running:
                    # Если уже запланировано обновление, не запускаем новое
                    if not self.update_scheduled:
                        self.update_plot()
                else:
                    self.draw_loaded_graph()
                    
    def on_adc_settings_changed(self):
        """Обработчик изменения настроек АЦП"""
        self.base.adc_params.bits = self.base.adc_settings.bits
        self.base.adc_params.ref_voltage = self.base.adc_settings.ref_voltage
        
        # Обновление буферов напряжения
        for tag, buffer in self.base.data_buffers.items():
            if buffer.count > 0:
                voltage_data = [self.base.adc_params.raw_to_voltage(v) 
                              for v in buffer.raw_data]
                buffer.voltage_data = voltage_data
                
        # Обновляем график
        if self.base.program_running:
            self.update_plot()
        elif any(buffer.count > 0 for buffer in self.base.data_buffers.values()):
            self.draw_loaded_graph()
            
        self.base.adc_settings.update_info()
        
    def load_graph(self):
        """Загрузка данных из файла"""
        if self.base.program_running:
            messagebox.showwarning("Внимание", "Невозможно загрузить график во время работы мониторинга!")
            return
        
        from tkinter import filedialog
        files = filedialog.askopenfilenames(filetypes=[("CSV", "*.csv")])
        if not files:
            return
        
        for file in files:
            name, raw_data, color = self.file_manager.load_data(file, self.base.adc_params)
            if raw_data:
                tag = os.path.splitext(os.path.basename(name))[0]
                # Создаем новый буфер
                self.base.data_buffers[tag] = DataBuffer(max_points=0)
                
                for raw_value in raw_data:
                    voltage = self.base.adc_params.raw_to_voltage(raw_value)
                    self.base.data_buffers[tag].add_point(raw_value, voltage)
                
                self.base.colors[tag] = color
                self.base.logger.log(f"[INFO] Загружено {len(raw_data)} значений: {tag}")
            
        self.draw_loaded_graph()
        
    def clear_graph(self):
        """Очистка графика"""
        if self.base.program_running:
            messagebox.showwarning("Внимание", "Невозможно очистить график во время работы мониторинга!")
            return
        
        for buffer in self.base.data_buffers.values():
            buffer.clear()
        
        self.base.colors.clear()
        self.base.plot_manager.clear_plot()
        self.base.main_window.canvas.draw()
        self.base.logger.log("[INFO] График очищен")
        
    def toggle_display_mode(self):
        """Переключение режима отображения графика между напряжением и дискретными значениями"""
        if self.base.program_running:
            messagebox.showwarning("Внимание", "Невозможно переключить график во время работы мониторинга!")
            return
            
        self.show_voltage = not self.show_voltage
        
        if self.base.program_running:
            self.update_plot()
        else:
            if any(buffer.count > 0 for buffer in self.base.data_buffers.values()):
                self.draw_loaded_graph()
        
        mode = "напряжение" if self.show_voltage else "дискретные значения"
        self.base.logger.log(f"[INFO] Режим отображения графика изменен: {mode}")