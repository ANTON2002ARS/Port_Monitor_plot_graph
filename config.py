"""Конфигурационные константы приложения"""

BAUDRATES = [
    1200, 2400, 4800,
    9600, 14400, 19200,
    28800, 38400, 56000,
    57600, 76800,
    115200, 128000, 230400,
    256000, 460800, 921600
]

ADC_BITS_OPTIONS = [8, 10, 12]
REF_VOLTAGE_OPTIONS = [3.3, 5.0]
PORT_TAGS = ["PORT1", "PORT2", "PORT3", "PORT4"]
MAX_POINTS = 300

# Цвета по умолчанию для портов
DEFAULT_COLORS = {
    "PORT1": "red",
    "PORT2": "green", 
    "PORT3": "blue",
    "PORT4": "orange"
}

# Стили кнопок
BUTTON_STYLE = {
    "bg": "white",
    "fg": "black",
    "font": ("Arial", 10),
    "bd": 2,
    "relief": "raised",
    "padx": 5,
    "pady": 2
}