## @file nuevo_atleta_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QDateEdit, QComboBox, QPushButton, QMessageBox)
from PySide6.QtCore import QDate
from models.atleta import Atleta

class NuevoAtletaDialog(QDialog):
    def __init__(self, localidad_repo, atleta=None, parent=None):
        super().__init__(parent)
        self.localidad_repo = localidad_repo
        self.atleta = atleta
        self.atleta_creado = None
        
        if self.atleta:
            self.setWindowTitle("Editar Atleta")
        else:
            self.setWindowTitle("Registrar Nuevo Atleta")
        self.setFixedWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Campos de texto simples
        self.input_dni = self._add_field(layout, '<html><font color="red">*</font> DNI:</html>')
        self.input_apellido = self._add_field(layout, '<html><font color="red">*</font> Apellido:</html>')
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

        # Género (Selector)
        layout.addWidget(QLabel("Género:"))
        self.combo_genero = QComboBox()
        self.combo_genero.addItem("Masculino", "M")
        self.combo_genero.addItem("Femenino", "F")
        layout.addWidget(self.combo_genero)

        # Provincia e Invitado
        layout.addWidget(QLabel("Provincia (o procedencia si es invitado):"))
        self.input_provincia = QLineEdit("Misiones")
        layout.addWidget(self.input_provincia)

        self.input_club = self._add_field(layout, "Club / Institución:")

        # Botones
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Guardar Atleta")
        btn_save.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_save.setDefault(True)
        btn_save.clicked.connect(self.validar_y_guardar)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

        # Si estamos editando, rellenamos los datos
        if self.atleta:
            self.input_dni.setText(self.atleta.dni)
            self.input_apellido.setText(self.atleta.apellido)
            self.input_nombre.setText(self.atleta.nombre)
            
            if self.atleta.fecha_nacimiento:
                qdate = QDate.fromString(self.atleta.fecha_nacimiento, "yyyy-MM-dd")
                if qdate.isValid():
                    self.input_fecha.setDate(qdate)
            
            idx = self.combo_localidad.findData(self.atleta.id_localidad)
            if idx >= 0:
                self.combo_localidad.setCurrentIndex(idx)
                
            idx_g = self.combo_genero.findData(self.atleta.genero)
            if idx_g >= 0:
                self.combo_genero.setCurrentIndex(idx_g)
                
            self.input_provincia.setText(self.atleta.provincia)
            self.input_club.setText(self.atleta.club)
            btn_save.setText("Guardar Cambios")

    def _add_field(self, layout, label_text):
        layout.addWidget(QLabel(label_text))
        field = QLineEdit()
        layout.addWidget(field)
        return field

    def validar_y_guardar(self):
        if not self.input_dni.text() or not self.input_apellido.text():
            QMessageBox.warning(self, "Error", "DNI y Apellido son obligatorios.")
            return

        id_atleta = self.atleta.id_atleta if self.atleta else None

        self.atleta_creado = Atleta(
            id_atleta=id_atleta,
            dni=self.input_dni.text(),
            apellido=self.input_apellido.text(),
            nombre=self.input_nombre.text(),
            fecha_nacimiento=self.input_fecha.date().toString("yyyy-MM-dd"),
            genero=self.combo_genero.currentData(),
            id_localidad=self.combo_localidad.currentData(),
            provincia=self.input_provincia.text(),
            club=self.input_club.text()
        )
        self.accept()