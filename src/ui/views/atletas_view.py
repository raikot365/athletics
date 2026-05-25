import sqlite3
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QPushButton, QLabel, QHeaderView, QDialog, QMessageBox)
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
        
        self.btn_nuevo = QPushButton("Registrar Atleta")
        self.btn_nuevo.setStyleSheet("background-color: #2c3e50; color: white; padding: 8px;")
        self.btn_nuevo.clicked.connect(self.abrir_registro)

        top_layout.addWidget(self.input_busqueda)
        top_layout.addWidget(self.btn_nuevo)
        layout.addLayout(top_layout)

        # Tabla
        self.tabla = QTableWidget(0, 9)
        self.tabla.setHorizontalHeaderLabels(["DNI", "Apellido", "Nombre", "Fecha de Nacimiento", "Género", "Provincia", "Localidad", "Club", "Acciones"])
        
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # DNI
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Apellido
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Nombre
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # Fecha de Nacimiento
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Género
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Provincia
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Localidad
        header.setSectionResizeMode(7, QHeaderView.Stretch)          # Club
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents) # Acciones
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
            
            genero_str = "Masculino" if a.genero == "M" else "Femenino"
            self.tabla.setItem(row, 3, QTableWidgetItem(a.fecha_nacimiento))
            self.tabla.setItem(row, 4, QTableWidgetItem(genero_str))
            self.tabla.setItem(row, 5, QTableWidgetItem(a.provincia))
            self.tabla.setItem(row, 6, QTableWidgetItem(self.localidad_repo.get_nombre(a.id_localidad)))
            self.tabla.setItem(row, 7, QTableWidgetItem(a.club))

            # Botones de Acciones
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setToolTip("Editar Atleta")
            btn_edit.setFixedWidth(30)
            btn_edit.clicked.connect(lambda checked=False, athlete=a: self.abrir_editar(athlete))
            
            btn_delete = QPushButton("🗑️")
            btn_delete.setToolTip("Eliminar Atleta")
            btn_delete.setFixedWidth(30)
            btn_delete.clicked.connect(lambda checked=False, athlete_id=a.id_atleta: self.confirmar_eliminacion(athlete_id))
            
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            actions_layout.addStretch()
            
            self.tabla.setCellWidget(row, 8, actions_widget)

    def abrir_registro(self):
        dialog = NuevoAtletaDialog(self.localidad_repo, parent=self)
        if dialog.exec() == QDialog.Accepted:
            try:
                self.atleta_repo.crear(dialog.atleta_creado)
                self.cargar_atletas()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error de Registro", "Ya existe un atleta registrado con este DNI.")

    def abrir_editar(self, atleta):
        dialog = NuevoAtletaDialog(self.localidad_repo, atleta=atleta, parent=self)
        if dialog.exec() == QDialog.Accepted:
            try:
                self.atleta_repo.actualizar(dialog.atleta_creado)
                self.cargar_atletas()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error de Edición", "No se pudo actualizar el atleta. El DNI ingresado ya está registrado para otro atleta.")

    def confirmar_eliminacion(self, athlete_id):
        res = QMessageBox.question(
            self, 
            "Confirmar Eliminación", 
            "¿Está seguro de que desea eliminar a este atleta? Se perderán todas sus participaciones y resultados en torneos.",
            QMessageBox.Yes | QMessageBox.No
        )
        if res == QMessageBox.Yes:
            try:
                self.atleta_repo.eliminar(athlete_id)
                self.cargar_atletas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el atleta:\n{str(e)}")
    