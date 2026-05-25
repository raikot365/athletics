## @file main.py
#  @brief Punto de entrada principal en la raíz del proyecto.

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# --- AGREGAR LA CARPETA 'src' AL PATH DE PYTHON ---
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# --- GESTIÓN DE RUTAS PARA RECURSOS (LOGO) ---
def resource_path(relative_path):
    """ Gestiona rutas para archivos internos en el .exe y desarrollo. """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Importamos desde la carpeta 'src'
from database.database_manager import DatabaseManager
from ui.main_window import MainWindow

def bootstrap():
    """ Inicializa la base de datos antes de arrancar. """
    # Se crea en la raíz junto al ejecutable/script
    db_manager = DatabaseManager("atletismo_misiones.db")
    
    # IMPORTANTE: Verifica si tu método es 'inicializar_base_datos' 
    # o 'inicializar_base_de_datos' según tu DatabaseManager.
    db_manager.inicializar_base_de_datos()
    
    return db_manager

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 

    # --- CONFIGURAR LOGO ---
    # Asumimos que el logo está en src/assets/logo.png
    logo_path = resource_path(os.path.join("assets", "logo.png"))
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))

    # Iniciar servicios e interfaz
    db_manager = bootstrap()
    window = MainWindow(db_manager)
    window.setWindowTitle("Atletismo v1.1")
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()