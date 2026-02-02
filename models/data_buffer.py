"""Буфер для хранения данных"""

class DataBuffer:
    def __init__(self, max_points=0):  # Изменено: по умолчанию 0 = без ограничений
        self.max_points = max_points
        self.raw_data = []
        self.voltage_data = []
        
    def add_point(self, raw_value, voltage):
        """Добавление точки данных"""
        self.raw_data.append(raw_value)
        self.voltage_data.append(voltage)
        
        # Ограничиваем размер буфера только если max_points > 0
        if self.max_points > 0 and len(self.raw_data) > self.max_points:
            self.raw_data = self.raw_data[-self.max_points:]
            self.voltage_data = self.voltage_data[-self.max_points:]
            
    def clear(self):
        """Очистка буфера"""
        self.raw_data.clear()
        self.voltage_data.clear()
        
    def get_voltage_view(self):
        """Получение представления для графика - ВСЕ данные"""
        return self.voltage_data if self.voltage_data else []
    
    def get_raw_view(self):
        """Получение сырых данных - ВСЕ данные"""
        return self.raw_data if self.raw_data else []
    
    @property
    def count(self):
        return len(self.raw_data)
    
    @property
    def last_raw_value(self):
        return self.raw_data[-1] if self.raw_data else 0
    
    @property
    def last_voltage(self):
        return self.voltage_data[-1] if self.voltage_data else 0