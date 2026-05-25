## @file nueva_prueba_dialog.py
#  @brief Formulario emergente para registrar una prueba deportiva.

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, 
                             QPushButton, QMessageBox)
from models.prueba import Prueba

class NuevaPruebaDialog(QDialog):
    """
    Ventana para capturar los datos de una nueva prueba vinculada a un torneo.
    """
    def __init__(self, id_torneo, prueba=None, parent=None):
        super().__init__(parent)
        self.id_torneo = id_torneo
        self.prueba = prueba
        self.prueba_creada = None
        
        if self.prueba:
            self.setWindowTitle("Editar Prueba")
        else:
            self.setWindowTitle("Crear Nueva Prueba")
        self.setFixedSize(350, 250)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # --- Nombre de la Prueba ---
        layout.addWidget(QLabel('<html><font color="red">*</font> Nombre de la Prueba:</html>'))
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Ej: 100m Llanos, 400m con Vallas...")
        layout.addWidget(self.input_nombre)

        # --- Categoría ---
        layout.addWidget(QLabel("Categoría:"))
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(["U12", "U14", "U16", "U18", "U20", "U23","Mayores", "Master"])
        self.combo_categoria.setEditable(True) # Permite escribir si no está en la lista
        layout.addWidget(self.combo_categoria)

        # --- Sexo ---
        layout.addWidget(QLabel("Sexo / Género de la Prueba:"))
        self.combo_sexo = QComboBox()
        self.combo_sexo.addItem("Masculino", "M")
        self.combo_sexo.addItem("Femenino", "F")
        layout.addWidget(self.combo_sexo)

        layout.addStretch()

        # --- Botones Guardar / Cancelar ---
        btn_layout = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold;")
        self.btn_guardar.setDefault(True)
        
        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_guardar)
        layout.addLayout(btn_layout)

        # Conexiones
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_guardar.clicked.connect(self.validar_y_guardar)

        # Si estamos editando, rellenamos los datos
        if self.prueba:
            self.input_nombre.setText(self.prueba.nombre)
            idx_cat = self.combo_categoria.findText(self.prueba.categoria)
            if idx_cat >= 0:
                self.combo_categoria.setCurrentIndex(idx_cat)
            else:
                self.combo_categoria.setEditText(self.prueba.categoria)
                
            idx_sex = self.combo_sexo.findData(self.prueba.sexo)
            if idx_sex >= 0:
                self.combo_sexo.setCurrentIndex(idx_sex)
            self.btn_guardar.setText("Guardar Cambios")

    def validar_y_guardar(self):
        nombre = self.input_nombre.text().strip()
        
        if not nombre:
            QMessageBox.warning(self, "Error", "Debe ingresar el nombre de la prueba.")
            return

        categoria = self.combo_categoria.currentText()
        sexo = self.combo_sexo.currentData() # Obtiene la "M", "F" o "X"

        id_prueba = self.prueba.id_prueba if self.prueba else None

        # Construir el objeto Prueba
        self.prueba_creada = Prueba(
            id_prueba=id_prueba,
            nombre=nombre,
            categoria=categoria,
            sexo=sexo,
            id_torneo=self.id_torneo
        )
        
        self.accept()