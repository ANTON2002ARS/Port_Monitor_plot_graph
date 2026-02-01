import atexit
import signal
import sys
from controllers.app_controller import AppController
from views.main_window import MainWindow
from views.port_settings import PortSettingsView
from views.adc_settings import ADCSettingsView
from views.control_panel import ControlPanel
from views.console import ConsoleView
from utils.logger import Logger

def main():
    """Основная функция приложения"""
    # Создание контроллера
    controller = AppController()
    
    # Создание представлений
    main_window = MainWindow(controller)
    port_settings = PortSettingsView(controller)
    adc_settings = ADCSettingsView(controller)
    control_panel = ControlPanel(controller)
    console = ConsoleView()
    
    # Настройка логгера
    logger = Logger()
    logger.set_callback(console.log)
    controller.logger = logger
    
    # Инициализация контроллера
    controller.init_views(main_window, port_settings, adc_settings, control_panel, console)
    
    # Настройка интерфейса
    main_window.setup_ui(port_settings, adc_settings, control_panel, console)
    
    # Обновление списка портов при запуске
    controller.refresh_ports()
    
    # Логирование информации
    logger.log("="*60)
    #logger.log("ADC Monitor")
    logger.log("Программа для мониторинга АЦП")
    logger.log(f"Текущие настройки: {controller.adc_params.bits} бит, {controller.adc_params.ref_voltage}В")
    logger.log(f"Диапазон АЦП: 0-{controller.adc_params.max_value}")
    logger.log("Формат данных с порта: ADC,<значение>")
    logger.log("="*60)
    
    # Регистрация обработчиков завершения
    atexit.register(controller.cleanup_resources)
    
    # Запуск приложения
    try:
        main_window.start()
    except KeyboardInterrupt:
        print("\n[INFO] Программа прервана пользователем")
    finally:
        controller.cleanup_resources()
        print("[INFO] Программа завершена")

if __name__ == "__main__":
    main()