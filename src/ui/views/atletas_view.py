## @file atletas_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QPushButton, QLabel, QHeaderView, QDialog)
from ui.views.dialogs.nuevo_atleta_dialog import NuevoAtletaDialog

class AtletasView(QWidget):
    def __init__(self, atleta_repo, localidad_repo):
        super().__init__()
        self.atleta_repo = atleta_repo
        self.localidad_repo = localidad_repo
        self._setup_ui()
        self.cargar_atletas()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Barra Superior
        top_layout = QHBoxLayout()
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por DNI, Nombre o Apellido...")
        self.input_busqueda.textChanged.connect(self.cargar_atletas)
        
        self.btn_nuevo = QPushButton("+ Registrar Atleta")
        self.btn_nuevo.setStyleSheet("background-color: #2c3e50; color: white; padding: 8px;")
        self.btn_nuevo.clicked.connect(self.abrir_registro)

        top_layout.addWidget(self.input_busqueda)
        top_layout.addWidget(self.btn_nuevo)
        layout.addLayout(top_layout)

        # Tabla
        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(["DNI", "Apellido", "Nombre", "Provincia", "Club"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla)

    def cargar_atletas(self):
        texto = self.input_busqueda.text()
        atletas = self.atleta_repo.buscar_filtrado(texto)
        self.tabla.setRowCount(0)
        for row, a in enumerate(atletas):
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(a.dni))
            self.tabla.setItem(row, 1, QTableWidgetItem(a.apellido))
            self.tabla.setItem(row, 2, QTableWidgetItem(a.nombre))
            self.tabla.setItem(row, 3, QTableWidgetItem(a.provincia)) # Podrías traer el nombre de la localidad con un JOIN luego
            self.tabla.setItem(row, 4, QTableWidgetItem(a.club))

    def abrir_registro(self):
        dialog = NuevoAtletaDialog(self.localidad_repo, self)
        if dialog.exec() == QDialog.Accepted:
            self.atleta_repo.crear(dialog.atleta_creado)
            self.cargar_atletas()