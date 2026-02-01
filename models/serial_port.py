"""Модель настроек последовательного порта"""

class SerialPortSettings:
    def __init__(self, tag, port="", baudrate=115200):
        self.tag = tag
        self.port = port
        self.baudrate = baudrate
        self.use_port = False if tag in ["PORT3", "PORT4"] else True  # PORT3,4 выключены по умолчанию
        self.auto_save = True
        self.color = None
        
    def to_dict(self):
        return {
            "tag": self.tag,
            "port": self.port,
            "baudrate": self.baudrate,
            "use_port": self.use_port,
            "auto_save": self.auto_save,
            "color": self.color
        }