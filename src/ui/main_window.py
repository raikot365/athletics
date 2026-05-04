# @file main_window.py
#  @brief Ventana principal de la aplicación con navegación lateral.

from database.repositories.localidad_repository import LocalidadRepository
from database.repositories.participacion_repository import ParticipacionRepository
from src.ui.views.torneos_view import TorneosView
from database.repositories.torneo_repository import TorneoRepository
from database.repositories.prueba_repository import PruebaRepository
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QStackedWidget, 
                             QFrame, QLabel)
from PySide6.QtCore import Qt
from ui.views.atletas_view import AtletasView
from database.repositories.atleta_repository import AtletaRepository
class MainWindow(QMainWindow):
    """
    Clase principal que gestiona el Sidebar y el intercambio de vistas.
    """
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.atleta_repo = AtletaRepository(self.db_manager)
        self.localidad_repo = LocalidadRepository(self.db_manager)
        self.torneo_repo = TorneoRepository(self.db_manager)
        self.prueba_repo = PruebaRepository(self.db_manager)
        self.participacion_repo = ParticipacionRepository(self.db_manager)

        self.setWindowTitle("Sistema de Gestión de Atletismo - Misiones")
        self.resize(1100, 700)

        # Widget central y layout horizontal principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Inicializar componentes
        self._setup_sidebar()
        self._setup_main_area()

    def _setup_sidebar(self):
        """
        Configura el panel lateral izquierdo.
        """
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setObjectName("sidebar")
        # Estilo básico (luego puedes moverlo a un archivo .qss)
        self.sidebar.setStyleSheet("""
            #sidebar { background-color: #2c3e50; }
            QPushButton { 
                color: white; border: none; padding: 15px; 
                text-align: left; font-size: 14px;
            }
            QPushButton:hover { background-color: #34495e; }
            QPushButton#active { background-color: #3498db; font-weight: bold; }
        """)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 0)
        sidebar_layout.setSpacing(5)

        # Botones del menú
        self.btn_atletas = QPushButton("  Atletas")
        self.btn_torneos = QPushButton("  Torneos")
        # self.btn_config = QPushButton("  Configuración")

        # Añadir botones al layout
        sidebar_layout.addWidget(self.btn_atletas)
        sidebar_layout.addWidget(self.btn_torneos)
        sidebar_layout.addStretch() # Empuja el resto hacia abajo
        # sidebar_layout.addWidget(self.btn_config)

        self.main_layout.addWidget(self.sidebar)

        # Conectar señales
        self.btn_atletas.clicked.connect(lambda: self.display_page(0))
        self.btn_torneos.clicked.connect(lambda: self.display_page(1))

    def _setup_main_area(self):
        """
        Configura el área de contenido dinámico.
        """
        self.content_stack = QStackedWidget()
        
        # Página 0: Gestión de Atletas (Placeholder)
        self.view_atletas = AtletasView(self.atleta_repo, self.localidad_repo)
        

        # Página 1: Gestión de Torneos (Placeholder)
        self.view_torneos = TorneosView(
            self.torneo_repo, 
            self.prueba_repo, 
            self.atleta_repo, 
            self.participacion_repo
        )

        # Añadir páginas al stack
        self.content_stack.addWidget(self.view_atletas)
        self.content_stack.addWidget(self.view_torneos)
        
        self.main_layout.addWidget(self.content_stack)

    def display_page(self, index: int):
        """
        Cambia la página visible en el stack.
        @param index Índice de la página a mostrar.
        """
        self.content_stack.setCurrentIndex(index)
        self._update_button_styles(index)

    def _update_button_styles(self, current_index: int):
        """
        Resalta visualmente el botón seleccionado.
        """
        # Limpiar estilos anteriores
        for i, btn in enumerate([self.btn_atletas, self.btn_torneos]):
            btn.setObjectName("active" if i == current_index else "")
            btn.style().unpolish(btn) # Refrescar estilo
            btn.style().polish(btn)