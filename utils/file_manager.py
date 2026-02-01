"""Менеджер для работы с файлами"""

import csv
from tkinter import filedialog
import os

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
            file = f"{tag}_adc_data.csv"
            
        try:
            with open(file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["color", color])
                writer.writerow(["value"])
                
                for raw_value in raw_data:
                    writer.writerow([int(raw_value)])
                    
            return file
        except Exception as e:
            return None
            
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
            return None, [], "blue"