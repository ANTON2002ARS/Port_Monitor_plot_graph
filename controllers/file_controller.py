"""Контроллер для управления файлами и настройками"""

from tkinter import messagebox
from utils.file_manager import FileManager

class FileController:
    """Управление файловыми операциями и настройками"""
    
    def __init__(self, base_controller):
        self.base = base_controller
        self.file_manager = FileManager()
        
    def refresh_ports(self):
        """Обновление списка портов"""
        if self.base.program_running:
            messagebox.showwarning("Внимание", "Невозможно обновить список портов во время работы мониторинга!")
            return
            
        ports = self.base.get_com_ports()
        self.base.sensor_settings.update_port_list(ports)
        self.base.logger.log(f"[INFO] Список портов обновлен. Доступно портов: {len(ports)}")
        
    def copy_log(self):
        """Копирование лога в буфер обмена"""
        self.base.main_window.root.clipboard_clear()
        self.base.main_window.root.clipboard_append(self.base.console.get_text())
        self.base.logger.log("[INFO] Лог скопирован в буфер обмена")
        
    def save_sensor_data(self, tag, ask_filename=True):
        """Сохранение данных сенсора"""
        if self.base.program_running:
            messagebox.showwarning("Внимание", "Невозможно сохранить данные во время работы мониторинга!")
            return
            
        if tag in self.base.data_buffers and self.base.data_buffers[tag].count > 0:
            color = self.base.colors.get(tag, "blue")
            saved_file = self.file_manager.save_data(tag, self.base.data_buffers[tag].raw_data, color, ask_filename)
            if saved_file:
                self.base.logger.log(f"[INFO] Данные сенсора {tag} сохранены в {saved_file} ({self.base.data_buffers[tag].count} значений)")
            else:
                messagebox.showerror("Ошибка", f"Не удалось сохранить данные сенсора {tag}")
        else:
            messagebox.showwarning("Внимание", f"Нет данных для сохранения у сенсора {tag}")
        
    def show_about(self):
        """Показать информацию о программе"""
        about_text = f"""
        ADC Monitor
        
        Программа для мониторинга АЦП через COM порты.
        
        Текущие настройки:
        - Битность АЦП: {self.base.adc_params.bits} бит
        - Опорное напряжение: {self.base.adc_params.ref_voltage}В
        - Диапазон АЦП: 0-{self.base.adc_params.max_value}
        
        Данные:
        - В логе и сохранениях: сырые значения АЦП
        - На графике: напряжение (0-{self.base.adc_params.ref_voltage}В)
        
        Формула преобразования для графика:
        Напряжение(V) = (ADC_RAW / {self.base.adc_params.max_value}) * {self.base.adc_params.ref_voltage}
        
        Формат данных с порта:
        ADC,<значение от 0 до {self.base.adc_params.max_value}>
        
        Например: ADC,512
        """
        messagebox.showinfo("О программе", about_text)