"""Контроллер для управления мониторингом сенсоров"""

import threading
import serial
import time
from tkinter import messagebox
from config import SENSOR_TAGS

class MonitoringController:
    """Управление мониторингом данных с COM портов"""
    
    def __init__(self, base_controller):
        self.base = base_controller
        self.selected_sensors = []
        
    def start_monitoring(self):
        """Запуск мониторинга"""
        if self.base.program_running:
            return
            
        # Проверяем выбранные сенсоры
        selected_sensors = []
        for tag in SENSOR_TAGS:
            settings = self.base.sensor_settings.get_sensor_settings(tag)
            if settings and settings['use_sensor'] and settings['port']:
                selected_sensors.append(tag)
                
        if not selected_sensors:
            messagebox.showerror("Ошибка", "Выберите хотя бы один сенсор")
            return
            
        # Сохраняем список выбранных сенсоров
        self.selected_sensors = selected_sensors.copy()
            
        # Очистка графиков и данных
        self.base.stop_threads_flag = False
        self.base.active_sensors = set(selected_sensors)
        
        # Инициализация буферов
        for tag in selected_sensors:
            settings = self.base.sensor_settings.get_sensor_settings(tag)
            if settings:
                self.base.colors[tag] = settings['color']
                self.base.data_buffers[tag].clear()
                self.base.last_values[tag] = None
                
        # Обновление параметров АЦП
        self.base.adc_params.bits = self.base.adc_settings.bits
        self.base.adc_params.ref_voltage = self.base.adc_settings.ref_voltage
        
        # Блокировка настроек
        self.base.sensor_settings.lock_sensors()
        self.base.adc_settings.lock_settings()
        
        # Запуск потоков
        self.base.program_running = True
        
        for tag in selected_sensors:
            settings = self.base.sensor_settings.get_sensor_settings(tag)
            if settings:
                thread = threading.Thread(
                    target=self.read_com_port,
                    args=(settings['port'], settings['baudrate'], tag),
                    daemon=True
                )
                thread.start()
                self.base.threads[tag] = thread
                
        # Запускаем обновление графика
        if self.base.plot_controller:
            self.base.plot_controller.update_plot()
                
        # Логирование
        self.base.logger.log("="*50)
        self.base.logger.log("=== ЗАПУСК МОНИТОРИНГА АЦП ===")
        self.base.logger.log(f"Битность АЦП: {self.base.adc_params.bits} бит")
        self.base.logger.log(f"Опорное напряжение: {self.base.adc_params.ref_voltage}В")
        self.base.logger.log(f"Диапазон АЦП: 0-{self.base.adc_params.max_value}")
        self.base.logger.log(f"Активные сенсоры: {', '.join(selected_sensors)}")
        self.base.logger.log("="*50)
        
    def stop_monitoring(self):
        """Остановка мониторинга"""
        if not self.base.program_running:
            return
            
        self.base.program_running = False
        self.base.stop_threads_flag = True
        
        # Логирование
        self.base.logger.log("="*50)
        self.base.logger.log("=== ОСТАНОВКА МОНИТОРИНГА ===")
        
        # Ожидание завершения потоков
        for tag, thread in list(self.base.threads.items()):
            if thread.is_alive():
                thread.join(timeout=2.0)
                
        # Закрытие портов
        for tag, ser in list(self.base.serial_ports.items()):
            try:
                if ser and ser.is_open:
                    ser.close()
                    self.base.logger.log(f"[INFO] Закрыт порт {tag}")
            except Exception as e:
                self.base.logger.log(f"[ERROR] Ошибка закрытия порта {tag}: {e}")
                
        self.base.serial_ports.clear()
        self.base.threads.clear()
        
        # Автосохранение данных для сенсоров с включенным автосохранением
        saved_files = []
        for tag in self.selected_sensors:
            settings = self.base.sensor_settings.get_sensor_settings(tag)
            if settings and settings['auto_save']:
                if tag in self.base.data_buffers and self.base.data_buffers[tag].count > 0:
                    color = self.base.colors.get(tag, "blue")
                    # Сохраняем без запроса имени файла
                    saved_file = self.base.file_controller.file_manager.save_data(
                        tag, 
                        self.base.data_buffers[tag].raw_data, 
                        color, 
                        ask_filename=False
                    )
                    if saved_file:
                        saved_files.append({
                            'tag': tag,
                            'filename': saved_file,
                            'count': self.base.data_buffers[tag].count
                        })
                        self.base.logger.log(f"[AUTO-SAVE] Данные сенсора {tag} сохранены в {saved_file}")
        
        # Выводим отчет о сохраненных файлах
        if saved_files:
            self.base.logger.log("[AUTO-SAVE] Отчет о сохраненных файлах:")
            self.base.logger.log(f"Всего сохранено файлов: {len(saved_files)}")
            for file_info in saved_files:
                self.base.logger.log(f"  • {file_info['tag']}: {file_info['filename']} ({file_info['count']} значений)")
        else:
            self.base.logger.log("[AUTO-SAVE] Нет данных для автосохранения")
        
        # Разблокировка настроек
        self.base.sensor_settings.unlock_sensors()
        self.base.adc_settings.unlock_settings()
        
        # Очистка активных сенсоров
        self.base.active_sensors.clear()
        
    def read_com_port(self, port, baud, tag):
        """Чтение данных с COM порта (для сенсора)"""
        try:
            ser = serial.Serial(port, baud, timeout=0.2)
            self.base.serial_ports[tag] = ser
            self.base.logger.log(f"[INFO] {tag}: {port} @ {baud} - Ожидание данных АЦП...")
        except Exception as e:
            self.base.logger.log(f"[ERROR] {tag}: {port}: {e}")
            self.base.active_sensors.discard(tag)
            return
            
        while not self.base.stop_threads_flag and self.base.program_running:
            try:
                line = ser.readline().decode("utf-8").strip()
                if not line:
                    continue
                    
                raw_value = self.parse_value(line)
                if raw_value is None:
                    continue
                    
                # Преобразование в напряжение
                voltage = self.base.adc_params.raw_to_voltage(raw_value)
                
                # Сохранение данных
                self.base.data_buffers[tag].add_point(raw_value, voltage)
                
                # Сохраняем последнее значение для вывода в одну строку
                if not hasattr(self.base, 'last_values'):
                    self.base.last_values = {}
                    
                self.base.last_values[tag] = {
                    'raw': raw_value,
                    'voltage': voltage,
                    'timestamp': time.time()
                }
                
                # Выводим в одну строку только по истечении интервала
                current_time = time.time()
                if hasattr(self.base, 'last_update_time'):
                    if current_time - self.base.last_update_time >= self.base.update_interval:
                        self.print_combined_values()
                        self.base.last_update_time = current_time
                else:
                    self.base.last_update_time = current_time
                    
            except serial.SerialException as e:
                if "read failed" in str(e) or "closed" in str(e):
                    break
                else:
                    self.base.logger.log(f"[ERROR] {tag}: {e}")
                    break
            except Exception as e:
                self.base.logger.log(f"[ERROR] {tag}: {e}")
                break
                
        # Закрытие порта
        try:
            ser.close()
            self.base.serial_ports.pop(tag, None)
            self.base.active_sensors.discard(tag)
            if hasattr(self.base, 'last_values'):
                self.base.last_values[tag] = None
        except Exception as e:
            self.base.logger.log(f"[ERROR] Ошибка закрытия порта {tag}: {e}")
            
    def parse_value(self, line):
        """Парсинг строки данных"""
        parts = line.replace(" ", "").split(",")
        if len(parts) != 2:
            return None
            
        try:
            raw_value = float(parts[1])
            max_adc = self.base.adc_params.max_value
            
            if raw_value < 0 or raw_value > max_adc:
                self.base.logger.log(f"[WARNING] Значение вне диапазона 0-{max_adc}: {raw_value}")
                return None
                
            return raw_value
        except:
            return None
            
    def print_combined_values(self):
        """Вывод значений всех активных сенсоров в одну строку"""
        if not hasattr(self.base, 'last_values') or not hasattr(self.base, 'SENSOR_TAGS'):
            return
            
        parts = []
        for tag in self.base.SENSOR_TAGS:
            # Проверяем активен ли сенсор и есть ли у него данные
            if tag in self.base.active_sensors and tag in self.base.last_values and self.base.last_values[tag] is not None:
                raw = self.base.last_values[tag]['raw']
                voltage = self.base.last_values[tag]['voltage']
                # Формат: SENSOR_1: 235 (1.2V)
                parts.append(f"{tag}: {int(raw)} ({voltage:.3f}V)")
        
        if parts:
            combined_str = " | ".join(parts)
            self.base.logger.log(combined_str)