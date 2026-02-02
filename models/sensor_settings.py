"""Модель настроек сенсора"""

class SensorSettings:  # Изменено с SerialPortSettings
    def __init__(self, tag, port="", baudrate=115200):
        self.tag = tag
        self.port = port
        self.baudrate = baudrate
        self.use_sensor = False if tag in ["SENSOR_3", "SENSOR_4"] else True  # SENSOR_3,4 выключены по умолчанию
        self.auto_save = True
        self.color = None
        
    def to_dict(self):
        return {
            "tag": self.tag,
            "port": self.port,
            "baudrate": self.baudrate,
            "use_sensor": self.use_sensor,
            "auto_save": self.auto_save,
            "color": self.color
        }