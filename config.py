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
SENSOR_TAGS = ["SENSOR_1", "SENSOR_2", "SENSOR_3", "SENSOR_4"]

# Цвета по умолчанию для сенсоров (теперь в HEX формате для лучшей совместимости)
DEFAULT_COLORS = {
    "SENSOR_1": "#ff0000",  # RED
    "SENSOR_2": "#00ff00",  # GREEN
    "SENSOR_3": "#0000ff",  # BLUE
    "SENSOR_4": "#ffa500"   # ORANGE
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