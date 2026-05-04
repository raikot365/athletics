## @file nuevo_torneo_dialog.py
#  @brief Formulario emergente para crear un nuevo torneo.

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QSpinBox, QDateEdit, 
                             QPushButton, QMessageBox)
from PySide6.QtCore import QDate
from models.torneo import Torneo

class NuevoTorneoDialog(QDialog):
    """
    Ventana emergente que captura los datos para un nuevo torneo.
    """
    def __init__(self, torneo_repo, prueba_repo, atleta_repo, participacion_repo, parent=None):
        super().__init__(parent)
        self.repo = torneo_repo
        self.repo_prueba = prueba_repo
        self.atleta_repo = atleta_repo           
        self.participacion_repo = participacion_repo
        

        self.setWindowTitle("Crear Nuevo Torneo")
        self.setFixedSize(350, 250)
        self.torneo_creado = None # Aquí guardaremos el objeto si se guarda con éxito
        self.torneo_seleccionado_id = None
        self._setup_ui()
        # self.cargar_torneos()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # --- Nombre del Torneo ---
        layout.addWidget(QLabel("Nombre del Torneo:"))
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Ej: Campeonato Provincial U20")
        layout.addWidget(self.input_nombre)

        # --- Edición ---
        layout.addWidget(QLabel("Edición (Número):"))
        self.input_edicion = QSpinBox()
        self.input_edicion.setMinimum(1)
        self.input_edicion.setMaximum(100)
        self.input_edicion.setValue(1)
        layout.addWidget(self.input_edicion)

        # --- Fecha de Inicio ---
        layout.addWidget(QLabel("Fecha de Inicio:"))
        self.input_fecha = QDateEdit()
        self.input_fecha.setCalendarPopup(True) # Muestra un calendario al hacer clic
        self.input_fecha.setDate(QDate.currentDate()) # Fecha de hoy por defecto
        layout.addWidget(self.input_fecha)

        layout.addStretch()

        # --- Botones Guardar / Cancelar ---
        btn_layout = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        
        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_guardar)
        layout.addLayout(btn_layout)

        # --- Conexiones ---
        self.btn_cancelar.clicked.connect(self.reject) # Cierra el diálogo
        self.btn_guardar.clicked.connect(self.validar_y_guardar)

    def validar_y_guardar(self):
        """
        Valida que el formulario no esté vacío y crea el objeto Torneo.
        """
        nombre = self.input_nombre.text().strip()
        
        if not nombre:
            QMessageBox.warning(self, "Error de Validación", "El nombre del torneo es obligatorio.")
            return

        # Si todo está bien, construimos el modelo (convirtiendo QDate a string AAAA-MM-DD)
        fecha_str = self.input_fecha.date().toString("yyyy-MM-dd")
        
        self.torneo_creado = Torneo(
            nombre=nombre,
            edicion=self.input_edicion.value(),
            fecha_inicio=fecha_str
        )
        
        self.accept() # Cierra el diálogo indicando éxito (Devuelve QDialog.Accepted)