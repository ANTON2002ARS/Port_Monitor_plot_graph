"""Менеджер для работы с графиками"""

import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

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
        x_data_lengths = []  # Для определения максимальной длины данных
        
        # Сначала собираем информацию о данных
        for name, data_info in plot_data.items():
            if not data_info['data']:
                continue
            x_data_lengths.append(len(data_info['data']))
        
        # Определяем максимальную длину данных
        max_data_length = max(x_data_lengths) if x_data_lengths else 0
        
        # Строим график
        for name, data_info in plot_data.items():
            if not data_info['data']:
                continue
                
            # Создаем массив индексов для оси X
            x_indices = list(range(len(data_info['data'])))
            
            self.ax.plot(
                x_indices,  # Индексы по оси X
                data_info['data'], 
                label=name, 
                color=data_info['color'], 
                linewidth=1.5
            )
            all_voltage_data.extend(data_info['data'])
            
        # Настройка графика
        self.ax.set_title(title, fontsize=12, pad=10)
        self.ax.set_xlabel("Номер сообщения", fontsize=10)
        
        # Масштабирование по оси X - минимум отступов
        if max_data_length > 0:
            # Минимальные отступы (0.5% вместо 5%)
            padding = max_data_length * 0.005
            if padding < 2:  # Но не менее 2 единиц для очень коротких графиков
                padding = 2
            self.ax.set_xlim(-padding, max_data_length - 1 + padding)
        
        # Масштабирование по оси Y
        if all_voltage_data:
            min_val = min(all_voltage_data) if all_voltage_data else 0
            max_val = max(all_voltage_data) if all_voltage_data else self.adc_params.ref_voltage
            padding = max(0.1, (max_val - min_val) * 0.05)  # 5% от диапазона
            self.ax.set_ylim(min_val - padding, max_val + padding)
        else:
            self.ax.set_ylim(0, self.adc_params.ref_voltage)
            
        # Сетка
        self.ax.grid(True, which="major", linewidth=0.8, alpha=0.7)
        self.ax.grid(True, which="minor", linestyle="--", linewidth=0.4, alpha=0.5)
        self.ax.xaxis.set_minor_locator(AutoMinorLocator())
        self.ax.yaxis.set_minor_locator(AutoMinorLocator())
        
        # Легенда - внутри графика, чтобы не занимать место снаружи
        if plot_data:
            # Пытаемся разместить легенду в лучшем месте
            self.ax.legend(title="Сенсоры", loc='best', fontsize=9, title_fontsize=10)
            
        # Горизонтальные линии (только для режима напряжения)
        if "Напряжение" in title:
            ref_v = self.adc_params.ref_voltage
            # Линии делаем более тонкими и прозрачными
            self.ax.axhline(y=ref_v, color='gray', linestyle='--', alpha=0.3, linewidth=0.8)
            self.ax.axhline(y=ref_v/2, color='gray', linestyle=':', alpha=0.3, linewidth=0.8)
            self.ax.axhline(y=0, color='black', linestyle='-', alpha=0.2, linewidth=0.8)
        
        # Устанавливаем отступы для всего графика - меньше боковых отступов, больше места для графика
        # [left, bottom, right, top] в долях от размера фигуры
        # Уменьшаем боковые отступы для большего пространства графика
        self.fig.subplots_adjust(left=0.07, bottom=0.10, right=0.98, top=0.95)
        
        # Автоматически подгоняем макет, чтобы все элементы влезли
        self.fig.tight_layout(rect=[0.03, 0.03, 0.97, 0.97])
        
        self.canvas.draw()
        
    def clear_plot(self):
        """Очистка графика"""
        self.ax.clear()
        self.ax.set_title("ADC Monitor", fontsize=12, pad=10)
        self.ax.set_xlabel("Номер сообщения", fontsize=10)
        self.ax.set_ylabel("Напряжение, В", fontsize=10)
        
        # Устанавливаем начальные границы
        self.ax.set_xlim(-2, 10)  # Минимальные отступы
        self.ax.set_ylim(0, self.adc_params.ref_voltage)
        
        self.ax.grid(True)
        
        # Устанавливаем отступы как при обновлении
        self.fig.subplots_adjust(left=0.07, bottom=0.10, right=0.98, top=0.95)
        self.fig.tight_layout(rect=[0.03, 0.03, 0.97, 0.97])
        
        self.canvas.draw()