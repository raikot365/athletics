## @file main.py
#  @brief Punto de entrada principal de la App de Atletismo.

import sys
import os

# Asegurar que la carpeta 'src' esté en el path para las importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication
from src.database.database_manager import DatabaseManager
from src.ui.main_window import MainWindow

def bootstrap():
    """
    Inicializa los servicios esenciales antes de lanzar la interfaz.
    """
    # 1. Inicializar la base de datos
    # Si prefieres una ruta específica, cámbiala aquí
    db_manager = DatabaseManager("atletismo_misiones.db")
    db_manager.inicializar_base_de_datos()
    
    return db_manager

def main():
    # Crear la aplicación Qt
    app = QApplication(sys.argv)
    
    # Estilo general para la aplicación (opcional)
    app.setStyle("Fusion") 

    # Inicializar base de datos y obtener el manager
    db_manager = bootstrap()

    # Lanzar la ventana principal
    # Nota: Más adelante pasaremos el db_manager a la ventana
    # para que las vistas puedan acceder a los repositorios.
    window = MainWindow(db_manager)
    window.show()

    # Ejecutar el bucle de eventos
    sys.exit(app.exec())

if __name__ == "__main__":
    main()