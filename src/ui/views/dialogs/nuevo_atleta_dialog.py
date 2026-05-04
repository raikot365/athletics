## @file nuevo_atleta_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QDateEdit, QComboBox, QPushButton, QMessageBox)
from PySide6.QtCore import QDate
from models.atleta import Atleta

class NuevoAtletaDialog(QDialog):
    def __init__(self, localidad_repo, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Nuevo Atleta")
        self.setFixedWidth(400)
        self.localidad_repo = localidad_repo
        self.atleta_creado = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Campos de texto simples
        self.input_dni = self._add_field(layout, "DNI:")
        self.input_apellido = self._add_field(layout, "Apellido:")
        self.input_nombre = self._add_field(layout, "Nombre:")

        # Fecha de Nacimiento
        layout.addWidget(QLabel("Fecha de Nacimiento:"))
        self.input_fecha = QDateEdit()
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setMaximumDate(QDate.currentDate())
        layout.addWidget(self.input_fecha)

        # Localidad (Selector)
        layout.addWidget(QLabel("Localidad (Misiones):"))
        self.combo_localidad = QComboBox()
        localidades = self.localidad_repo.obtener_todas()
        for loc in localidades:
            self.combo_localidad.addItem(loc.nombre, loc.id_localidad)
        layout.addWidget(self.combo_localidad)

        # Provincia e Invitado
        layout.addWidget(QLabel("Provincia (o procedencia si es invitado):"))
        self.input_provincia = QLineEdit("Misiones")
        layout.addWidget(self.input_provincia)

        self.input_club = self._add_field(layout, "Club / Institución:")

        # Botones
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Guardar Atleta")
        btn_save.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_save.clicked.connect(self.validar_y_guardar)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def _add_field(self, layout, label_text):
        layout.addWidget(QLabel(label_text))
        field = QLineEdit()
        layout.addWidget(field)
        return field

    def validar_y_guardar(self):
        if not self.input_dni.text() or not self.input_apellido.text():
            QMessageBox.warning(self, "Error", "DNI y Apellido son obligatorios.")
            return

        self.atleta_creado = Atleta(
            dni=self.input_dni.text(),
            apellido=self.input_apellido.text(),
            nombre=self.input_nombre.text(),
            fecha_nacimiento=self.input_fecha.date().toString("yyyy-MM-dd"),
            id_localidad=self.combo_localidad.currentData(),
            provincia=self.input_provincia.text(),
            club=self.input_club.text()
        )
        self.accept()