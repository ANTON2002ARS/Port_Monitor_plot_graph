"""Менеджер для работы с графиками"""

import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from config import MAX_POINTS

class PlotManager:
    def __init__(self, fig, ax, canvas, adc_params):
        self.fig = fig
        self.ax = ax
        self.canvas = canvas
        self.adc_params = adc_params
        
    def update_plot(self, plot_data, title="ADC Monitor"):
        """Обновление графика"""
        self.ax.clear()
        
        # Собираем все данные для авто-масштабирования
        all_voltage_data = []
        
        for name, data_info in plot_data.items():
            if not data_info['data']:
                continue
                
            self.ax.plot(
                data_info['data'], 
                label=name, 
                color=data_info['color'], 
                linewidth=1.5
            )
            all_voltage_data.extend(data_info['data'])
            
        # Настройка графика
        self.ax.set_title(title)
        self.ax.set_xlabel("Номер сообщение")
        self.ax.set_ylabel("Напряжение, В")
        
        # Масштабирование
        if all_voltage_data:
            min_val = 0
            max_val = max(all_voltage_data)
            padding = max(0.1, max_val * 0.1)
            self.ax.set_ylim(min_val, max_val + padding)
        else:
            self.ax.set_ylim(0, self.adc_params.ref_voltage)
            
        # Сетка
        self.ax.grid(True, which="major", linewidth=0.8)
        self.ax.grid(True, which="minor", linestyle="--", linewidth=0.4)
        self.ax.xaxis.set_minor_locator(AutoMinorLocator())
        self.ax.yaxis.set_minor_locator(AutoMinorLocator())
        
        # Легенда
        if plot_data:
            self.ax.legend(title="COM Порты", loc='upper right')
            
        # Горизонтальные линии
        ref_v = self.adc_params.ref_voltage
        self.ax.axhline(y=ref_v, color='gray', linestyle='--', alpha=0.3, label=f'{ref_v}В')
        self.ax.axhline(y=ref_v/2, color='gray', linestyle=':', alpha=0.3, label=f'{ref_v/2:.1f}В')
        self.ax.axhline(y=0, color='black', linestyle='-', alpha=0.2)
        
        self.fig.tight_layout()
        self.canvas.draw()
        
    def clear_plot(self):
        """Очистка графика"""
        self.ax.clear()
        self.ax.set_title("ADC Monitor")
        self.ax.set_xlabel("Номер сообщение")
        self.ax.set_ylabel("Напряжение, В")
        self.ax.grid(True)
        self.canvas.draw()