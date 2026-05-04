## @file prueba_widget.py
#  @brief Widget expandible para gestionar una prueba específica y sus resultados.

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                             QLineEdit, QHeaderView, QFrame, QDialog, QMessageBox)
from PySide6.QtCore import Qt
from models.prueba import Prueba
from ui.views.dialogs.inscripcion_dialog import InscripcionDialog

class PruebaWidget(QFrame):
    """
    Widget tipo acordeón que gestiona los resultados de una prueba.
    """
    def __init__(self, prueba, atleta_repo, participacion_repo, parent=None):
        super().__init__(parent)
        self.prueba = prueba
        self.atleta_repo = atleta_repo
        self.participacion_repo = participacion_repo
        self.is_expanded = False

        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("pruebaWidget")
        self.setStyleSheet("""
            #pruebaWidget {
                border: 1px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                margin-bottom: 5px;
            }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._setup_header()
        self._setup_content()
        self.cargar_participantes()

    def _setup_header(self):
        """
        Crea la cabecera clickable del acordeón.
        """
        self.header_button = QPushButton(f"  ▶  {self.prueba.nombre} - {self.prueba.categoria} ({self.prueba.sexo})")
        self.header_button.setFixedHeight(40)
        self.header_button.setCursor(Qt.PointingHandCursor)
        self.header_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f6fa;
                border: none;
                text-align: left;
                font-weight: bold;
                font-size: 13px;
                color: #2f3640;
                border-bottom: 1px solid #dcdde1;
            }
            QPushButton:hover { background-color: #ebedf0; }
        """)
        self.header_button.clicked.connect(self.toggle_collapse)
        self.main_layout.addWidget(self.header_button)

    def _setup_content(self):
        """
        Crea el contenedor de resultados (inicialmente oculto).
        """
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)

        # --- Barra de Herramientas de la Prueba ---
        self.tools_layout = QHBoxLayout()

        # 1. Botón de Inscripción (Lado izquierdo)
        self.btn_abrir_inscripcion = QPushButton("+ Inscribir Atleta")
        self.btn_abrir_inscripcion.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 5px 10px;")
        self.btn_abrir_inscripcion.clicked.connect(self.abrir_inscripcion)
        self.tools_layout.addWidget(self.btn_abrir_inscripcion)

        # 2. Filtro de Instancia
        self.tools_layout.addSpacing(20)
        self.tools_layout.addWidget(QLabel("Filtrar:"))
        self.combo_instancia = QComboBox()
        self.combo_instancia.addItems(["Todas", "Final", "Serie 1", "Serie 2", "Serie 3", "Serie 4"])
        # Conectar el combo para que filtre cuando cambie (opcional, según tu lógica de carga)
        self.combo_instancia.currentTextChanged.connect(self.cargar_participantes)
        self.tools_layout.addWidget(self.combo_instancia)

        # Espaciador para empujar la carga rápida a la derecha
        self.tools_layout.addStretch()

        # --- SECCIÓN DE CARGA RÁPIDA ---
        self.tools_layout.addWidget(QLabel("<b>Carga rápida:</b>"))

        # Dorsal
        self.input_dorsal = QLineEdit()
        self.input_dorsal.setPlaceholderText("Dorsal")
        self.input_dorsal.setFixedWidth(50)
        # self.input_dorsal.setAlignment(Qt.AlignCenter)
        self.tools_layout.addWidget(self.input_dorsal)

        # 2. Instancia para la carga (Serie/Final)
        self.combo_carga_instancia = QComboBox()
        self.combo_carga_instancia.addItems(["Final", "Serie 1", "Serie 2", "Serie 3", "Serie 4"])
        self.combo_carga_instancia.setFixedWidth(80)
        self.tools_layout.addWidget(self.combo_carga_instancia)

        # Contenedor de Tiempo (MM:SS.CC)
        self.time_container = QWidget()
        self.time_layout = QHBoxLayout(self.time_container)
        self.time_layout.setContentsMargins(0,0,0,0)
        self.time_layout.setSpacing(2)

        self.input_mm = QLineEdit("00")
        self.input_ss = QLineEdit("00")
        self.input_cc = QLineEdit("00")

        for inp in [self.input_mm, self.input_ss, self.input_cc]:
            inp.setFixedWidth(30)
            inp.setAlignment(Qt.AlignCenter)
            inp.setMaxLength(2)

        self.time_layout.addWidget(self.input_mm)
        self.time_layout.addWidget(QLabel(":"))
        self.time_layout.addWidget(self.input_ss)
        self.time_layout.addWidget(QLabel("."))
        self.time_layout.addWidget(self.input_cc)

        self.tools_layout.addWidget(self.time_container)

        # Botón Cargar
        self.btn_cargar = QPushButton("Cargar")
        self.btn_cargar.clicked.connect(self.procesar_carga_resultado)
        self.btn_cargar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 5px 15px;")
        self.tools_layout.addWidget(self.btn_cargar)

        # Conexiones para UX de carga rápida
        self.input_mm.textChanged.connect(lambda t: self.input_ss.setFocus() if len(t) == 2 else None)
        self.input_ss.textChanged.connect(lambda t: self.input_cc.setFocus() if len(t) == 2 else None)
        self.input_cc.returnPressed.connect(self.procesar_carga_resultado)
        self.combo_instancia.currentTextChanged.connect(
    lambda t: self.combo_carga_instancia.setCurrentText(t) if t != "Todas" else None
)

        self.content_layout.addLayout(self.tools_layout)

        # --- Tabla de Resultados ---
        self.tabla_resultados = QTableWidget(0, 6)
        self.tabla_resultados.setHorizontalHeaderLabels([
            "Dorsal", "Atleta", "Instancia", "Resultado", "Posición", "Acciones"
        ])
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_resultados.setSelectionBehavior(QTableWidget.SelectRows)
        self.content_layout.addWidget(self.tabla_resultados)

        # Ocultar por defecto e insertar en el layout principal del Frame
        self.content_container.setVisible(False)
        self.main_layout.addWidget(self.content_container)

    def toggle_collapse(self):
        """
        Alterna la visibilidad de los resultados.
        """
        self.is_expanded = not self.is_expanded
        self.content_container.setVisible(self.is_expanded)
        icon = "  ▼ " if self.is_expanded else "  ▶ "
        self.header_button.setText(f"{icon} {self.prueba.nombre} - {self.prueba.categoria} ({self.prueba.sexo})")

    def abrir_inscripcion(self):
        dialog = InscripcionDialog(self.atleta_repo, self.participacion_repo, self.prueba.id_prueba, self)
        if dialog.exec() == QDialog.Accepted:
            inscripcion = dialog.resultado_inscripcion
            # 1. Guardar en BD usando el repo
            self.participacion_repo.inscribir_atleta(inscripcion)
            # 2. Refrescar la tabla del acordeón para que aparezca el atleta
            self.cargar_participantes()

    def cargar_participantes(self):
        """Refresca la tabla y calcula la posición dinámicamente."""
        instancia_filtro = self.combo_instancia.currentText()
        filtro = None if instancia_filtro == "Todas" else instancia_filtro

        participantes = self.participacion_repo.obtener_resultados_prueba(self.prueba.id_prueba, filtro)
        self.tabla_resultados.setRowCount(0)
        pos_contador = 1
        ultima_instancia_vista = None

        for row, p in enumerate(participantes):
            # LÓGICA DE REINICIO DE POSICIÓN:
            # Si la instancia cambia (ej: pasamos de 'Final' a 'Serie 1'), reiniciamos el podio
            if p.instancia != ultima_instancia_vista:
                pos_contador = 1
                ultima_instancia_vista = p.instancia

            self.tabla_resultados.insertRow(row)
            
            # Celdas básicas
            self.tabla_resultados.setItem(row, 0, QTableWidgetItem(str(p.numero_dorsal)))
            self.tabla_resultados.setItem(row, 1, QTableWidgetItem(f"{p.apellido}, {p.nombre}"))
            
            # Instancia (le damos un color diferente para resaltar el agrupamiento)
            item_instancia = QTableWidgetItem(p.instancia)
            if p.instancia == "Final":
                item_instancia.setForeground(Qt.darkBlue)
            self.tabla_resultados.setItem(row, 2, QTableWidgetItem(item_instancia))
            
            # Resultado
            tiempo = p.resultado if p.resultado else "---"
            self.tabla_resultados.setItem(row, 3, QTableWidgetItem(tiempo))
            
            # --- POSICIÓN DINÁMICA POR BLOQUE ---
            if p.resultado and p.resultado != "---" and p.resultado != "00:00.00":
                self.tabla_resultados.setItem(row, 4, QTableWidgetItem(f"{pos_contador}"))
                pos_contador += 1
            else:
                self.tabla_resultados.setItem(row, 4, QTableWidgetItem("-"))

            # Botón Eliminar
            btn_eliminar = QPushButton("🗑")
            btn_eliminar.setFixedWidth(30)
            btn_eliminar.clicked.connect(lambda ch=False, pid=p.id_participacion: self.confirmar_eliminacion(pid))
            self.tabla_resultados.setCellWidget(row, 5, btn_eliminar)

    def procesar_carga_resultado(self):
        """Captura los datos de los inputs y los manda al repositorio."""
        dorsal_str = self.input_dorsal.text().strip()
        instancia_carga = self.combo_carga_instancia.currentText()
        tiempo_str = f"{self.input_mm.text().zfill(2)}:{self.input_ss.text().zfill(2)}.{self.input_cc.text().zfill(2)}"

        # Validaciones básicas
        if not dorsal_str or not tiempo_str:
            return # No hacemos nada si están vacíos

        try:
            dorsal = int(dorsal_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "El dorsal debe ser un número.")
            return

        exito = self.participacion_repo.cargar_resultado_por_dorsal(
            self.prueba.id_prueba, 
            int(dorsal_str), 
            instancia_carga, 
            tiempo_str
        )

        if exito:
            # 1. Limpiar campos
            self.input_dorsal.clear()

            self.input_mm.setText("00")
            self.input_ss.setText("00")
            self.input_cc.setText("000")
            self.cargar_participantes()
            self.input_dorsal.setFocus()

        else:
            QMessageBox.warning(
                self, 
                "Error de carga", 
                f"No se encontró al atleta con dorsal {dorsal_str} en la instancia '{instancia_carga}'."
            )

    def confirmar_eliminacion(self, id_participacion):
        res = QMessageBox.question(self, "Confirmar", "¿Desea eliminar este atleta de la prueba?",
                                    QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            self.participacion_repo.eliminar_participacion(id_participacion)
            self.cargar_participantes()