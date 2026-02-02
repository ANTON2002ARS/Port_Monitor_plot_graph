"""Менеджер для работы с файлами"""

import csv
from tkinter import filedialog
import os
import time

class FileManager:
    def __init__(self):
        pass
        
    def save_data(self, tag, raw_data, color, ask_filename=True):
        """Сохранение данных в файл"""
        if not raw_data:
            return None
            
        if ask_filename:
            file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV", "*.csv")],
                title=f"Сохранение данных {tag}"
            )
            if not file:
                return None
        else:
            # Автосохранение: создаем имя файла с названием цвета в верхнем регистре
            color_name = self.get_color_name(color).upper()
            file = f"{tag}_data_{color_name}.csv"
            
        try:
            with open(file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["color", color])
                writer.writerow(["value"])
                
                for raw_value in raw_data:
                    writer.writerow([int(raw_value)])
                    
            return file
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")
            return None
    
    def get_color_name(self, color):
        """Получение названия цвета из hex или названия"""
        # Словарь соответствия hex кодов к названиям цветов
        color_map = {
            "#ff0000": "RED", "#ff4500": "ORANGERED", "#ff8c00": "DARKORANGE",
            "#ffa500": "ORANGE", "#ffff00": "YELLOW", "#9acd32": "YELLOWGREEN",
            "#00ff00": "GREEN", "#32cd32": "LIMEGREEN", "#00fa9a": "MEDIUMSPRINGGREEN",
            "#00ffff": "CYAN", "#00ced1": "DARKTURQUOISE", "#0000ff": "BLUE",
            "#1e90ff": "DODGERBLUE", "#00008b": "DARKBLUE", "#4b0082": "INDIGO",
            "#800080": "PURPLE", "#9400d3": "DARKVIOLET", "#ff00ff": "MAGENTA",
            "#ff1493": "DEEPPINK", "#ff69b4": "HOTPINK", "#c71585": "MEDIUMVIOLETRED",
            "#a0522d": "SIENNA", "#8b4513": "SADDLEBROWN", "#d2691e": "CHOCOLATE",
            "#808080": "GRAY", "#000000": "BLACK", "#ffffff": "WHITE"
        }
        
        # Если цвет в hex формате
        if color.startswith("#"):
            color = color.upper()
            # Ищем точное соответствие
            if color in color_map:
                return color_map[color]
            # Пытаемся приблизительно определить цвет
            try:
                # Преобразуем hex в RGB
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                
                # Определяем доминирующий цвет
                if r > 200 and g < 100 and b < 100:
                    return "RED"
                elif r < 100 and g > 200 and b < 100:
                    return "GREEN"
                elif r < 100 and g < 100 and b > 200:
                    return "BLUE"
                elif r > 200 and g > 200 and b < 100:
                    return "YELLOW"
                elif r > 200 and g < 100 and b > 200:
                    return "MAGENTA"
                elif r < 100 and g > 200 and b > 200:
                    return "CYAN"
                elif r > 200 and g > 100 and b < 100:
                    return "ORANGE"
                elif r > 200 and g > 200 and b > 200:
                    return "WHITE"
                elif r < 50 and g < 50 and b < 50:
                    return "BLACK"
                else:
                    # Возвращаем HEX без #
                    return color[1:]
            except:
                # Если не удалось распарсить hex, возвращаем без #
                return color.replace("#", "")
        else:
            # Если уже название цвета, возвращаем его
            return color
            
    def load_data(self, filename, adc_params):
        """Загрузка данных из файла"""
        name = os.path.basename(filename)
        raw_values = []
        color = "blue"
        
        try:
            with open(filename) as f:
                reader = csv.reader(f)
                
                # Читаем первую строку (цвет)
                try:
                    first_row = next(reader)
                    if first_row[0].lower() == "color":
                        color = first_row[1]
                        # Читаем вторую строку (заголовок "value")
                        second_row = next(reader)
                        if second_row[0].lower() == "value":
                            # Читаем остальные строки как значения
                            for r in reader:
                                if r:
                                    try:
                                        raw_value = float(r[0])
                                        raw_values.append(raw_value)
                                    except:
                                        continue
                    else:
                        # Старый формат
                        f.seek(0)
                        for r in reader:
                            if r:
                                try:
                                    raw_value = float(r[0])
                                    raw_values.append(raw_value)
                                except:
                                    continue
                except StopIteration:
                    # Файл пустой
                    pass
                    
            return name, raw_values, color
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            return None, [], "blue"