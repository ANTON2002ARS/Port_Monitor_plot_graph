"""Модель параметров АЦП"""

class ADCParameters:
    def __init__(self, bits=10, ref_voltage=5.0):
        self._bits = bits
        self._ref_voltage = ref_voltage
        self._max_value = 2 ** bits
        
    @property
    def bits(self):
        return self._bits
    
    @bits.setter
    def bits(self, value):
        self._bits = value
        self._max_value = 2 ** value
        
    @property
    def ref_voltage(self):
        return self._ref_voltage
    
    @ref_voltage.setter
    def ref_voltage(self, value):
        self._ref_voltage = value
        
    @property
    def max_value(self):
        return self._max_value
        
    def raw_to_voltage(self, raw_value):
        """Преобразование сырого значения в напряжение"""
        voltage = (raw_value / self.max_value) * self.ref_voltage
        return max(0, voltage)  # Гарантируем неотрицательное значение