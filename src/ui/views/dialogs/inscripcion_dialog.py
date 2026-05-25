## @file inscripcion_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHeaderView, QMessageBox)
from PySide6.QtCore import Qt

class InscripcionDialog(QDialog):
    def __init__(self, atleta_repo, participacion_repo, id_prueba, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inscribir Atleta a la Prueba")
        self.setFixedSize(500, 450)
        
        self.atleta_repo = atleta_repo
        self.participacion_repo = participacion_repo
        self.id_prueba = id_prueba
        self.atleta_seleccionado_id = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # --- Buscador de Atleta ---
        layout.addWidget(QLabel("<b>1. Buscar Atleta (DNI o Apellido):</b>"))
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Escriba para buscar...")
        self.input_buscar.textChanged.connect(self.actualizar_busqueda)
        layout.addWidget(self.input_buscar)

        self.tabla_busqueda = QTableWidget(0, 3)
        self.tabla_busqueda.setHorizontalHeaderLabels(["DNI", "Apellido", "Nombre"])
        self.tabla_busqueda.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_busqueda.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_busqueda.setFixedHeight(180)
        self.tabla_busqueda.itemSelectionChanged.connect(self.seleccionar_atleta)
        layout.addWidget(self.tabla_busqueda)

        # --- Datos de Inscripción ---
        layout.addWidget(QLabel("<b>2. Datos de Competencia:</b>"))
        
        form_layout = QHBoxLayout()
        
        # Dorsal
        vbox_dorsal = QVBoxLayout()
        vbox_dorsal.addWidget(QLabel("N° Dorsal:"))
        self.input_dorsal = QLineEdit()
        vbox_dorsal.addWidget(self.input_dorsal)
        form_layout.addLayout(vbox_dorsal)

        # Instancia (Serie)
        vbox_serie = QVBoxLayout()
        vbox_serie.addWidget(QLabel("Instancia/Serie:"))
        self.input_instancia = QLineEdit()
        self.input_instancia.setText("Final") # Valor por defecto
        vbox_serie.addWidget(self.input_instancia)
        form_layout.addLayout(vbox_serie)
        
        layout.addLayout(form_layout)
        layout.addStretch()

        # --- Botones ---
        btn_layout = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_inscribir = QPushButton("Confirmar Inscripción")
        self.btn_inscribir.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
        self.btn_inscribir.setEnabled(False)
        self.btn_inscribir.setDefault(True)
        
        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_inscribir)
        layout.addLayout(btn_layout)

        # Conexiones
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_inscribir.clicked.connect(self.guardar_inscripcion)

    def actualizar_busqueda(self):
        texto = self.input_buscar.text()
        if len(texto) < 2:
            self.tabla_busqueda.setRowCount(0)
            return
        
        instancia_actual = self.input_instancia.text()
        
        resultados = self.atleta_repo.buscar_para_inscripcion(texto, self.id_prueba, instancia_actual)
        
        self.tabla_busqueda.setRowCount(0)
        
        for row, res in enumerate(resultados):
            self.tabla_busqueda.insertRow(row)
            item_dni = QTableWidgetItem(str(res['dni']))
            item_dni.setData(Qt.UserRole, res['id_atleta']) # Guardamos el ID oculto
            self.tabla_busqueda.setItem(row, 0, item_dni)
            self.tabla_busqueda.setItem(row, 1, QTableWidgetItem(res['apellido']))
            self.tabla_busqueda.setItem(row, 2, QTableWidgetItem(res['nombre']))

    def seleccionar_atleta(self):
        items = self.tabla_busqueda.selectedItems()
        if items:
            self.atleta_seleccionado_id = items[0].data(Qt.UserRole)
            self.btn_inscribir.setEnabled(True)

    def guardar_inscripcion(self):
        dorsal = self.input_dorsal.text().strip()
        instancia = self.input_instancia.text().strip()

        if not self.atleta_seleccionado_id:
            QMessageBox.warning(self, "Error", "Debe seleccionar un atleta.")
            return

        dorsal_val = None
        if dorsal:
            try:
                dorsal_val = int(dorsal)
            except ValueError:
                QMessageBox.warning(self, "Error", "El dorsal debe ser un número entero.")
                return

        # Aquí llamaríamos al ParticipacionRepository para insertar
        from models.participacion import Participacion
        nueva_p = Participacion(
            id_atleta=self.atleta_seleccionado_id,
            id_prueba=self.id_prueba,
            instancia=instancia,
            numero_dorsal=dorsal_val
        )
        
        # Guardamos en una propiedad para que el widget padre la use
        self.resultado_inscripcion = nueva_p
        self.accept()