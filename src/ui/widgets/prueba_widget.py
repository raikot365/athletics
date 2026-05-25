## @file prueba_widget.py
#  @brief Widget expandible para gestionar una prueba específica y sus resultados.

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                             QLineEdit, QHeaderView, QFrame, QDialog, QMessageBox)
from PySide6.QtCore import Qt
from models.prueba import Prueba
from ui.views.dialogs.inscripcion_dialog import InscripcionDialog

class TimeInputField(QLineEdit):
    def focusInEvent(self, event):
        super().focusInEvent(event)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self.selectAll)

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
        Crea la cabecera clickable del acordeón con botones de acciones.
        """
        header_widget = QWidget()
        header_widget.setFixedHeight(40)
        header_widget.setStyleSheet("background-color: #f5f6fa; border-bottom: 1px solid #dcdde1;")
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 0, 5, 0)
        header_layout.setSpacing(2)
        
        # Botón del acordeón (título)
        self.header_button = QPushButton(f"  ▶  {self.prueba.nombre} - {self.prueba.categoria} ({self.prueba.sexo})")
        self.header_button.setCursor(Qt.PointingHandCursor)
        self.header_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                text-align: left;
                font-weight: bold;
                font-size: 13px;
                color: #2f3640;
            }
            QPushButton:hover { color: #2980b9; }
        """)
        self.header_button.clicked.connect(self.toggle_collapse)
        header_layout.addWidget(self.header_button, 1) # Estirar
        
        # Botón Editar Prueba
        self.btn_edit_prueba = QPushButton("✏️")
        self.btn_edit_prueba.setToolTip("Editar Prueba")
        self.btn_edit_prueba.setFixedWidth(30)
        self.btn_edit_prueba.setFixedHeight(30)
        self.btn_edit_prueba.setCursor(Qt.PointingHandCursor)
        self.btn_edit_prueba.setStyleSheet("QPushButton { border: none; background: transparent; } QPushButton:hover { background-color: #ebedf0; border-radius: 3px; }")
        self.btn_edit_prueba.clicked.connect(self.abrir_editar_prueba)
        header_layout.addWidget(self.btn_edit_prueba)
        
        # Botón Eliminar Prueba
        self.btn_delete_prueba = QPushButton("🗑️")
        self.btn_delete_prueba.setToolTip("Eliminar Prueba")
        self.btn_delete_prueba.setFixedWidth(30)
        self.btn_delete_prueba.setFixedHeight(30)
        self.btn_delete_prueba.setCursor(Qt.PointingHandCursor)
        self.btn_delete_prueba.setStyleSheet("QPushButton { border: none; background: transparent; } QPushButton:hover { background-color: #ebedf0; border-radius: 3px; }")
        self.btn_delete_prueba.clicked.connect(self.confirmar_eliminacion_prueba)
        header_layout.addWidget(self.btn_delete_prueba)
        
        self.main_layout.addWidget(header_widget)

    def _setup_content(self):
        """
        Crea el contenedor de resultados (inicialmente oculto).
        """
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)

        # --- Barra de Herramientas de la Prueba ---
        self.tools_layout = QHBoxLayout()

        # 1. Botón de Inscripción (Lado izquierdo)
        self.btn_abrir_inscripcion = QPushButton("Inscribir Atleta")
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

        self.input_mm = TimeInputField("00")
        self.input_ss = TimeInputField("00")
        self.input_cc = TimeInputField("00")

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
        self.tabla_resultados.itemChanged.connect(self.al_cambiar_item_tabla)
        self.tabla_resultados.setMinimumHeight(170)
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
        # Desconectar temporalmente la señal para evitar bucles durante la carga
        try:
            self.tabla_resultados.itemChanged.disconnect(self.al_cambiar_item_tabla)
        except TypeError:
            pass

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
            dorsal_str = str(p.numero_dorsal) if p.numero_dorsal is not None else "---"
            item_dorsal = QTableWidgetItem(dorsal_str)
            item_dorsal.setData(Qt.UserRole, p.id_participacion)
            item_dorsal.setFlags(item_dorsal.flags() | Qt.ItemIsEditable)
            self.tabla_resultados.setItem(row, 0, item_dorsal)
            
            item_nombre = QTableWidgetItem(f"{p.apellido}, {p.nombre}")
            item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemIsEditable)
            self.tabla_resultados.setItem(row, 1, item_nombre)
            
            # Instancia (le damos un color diferente para resaltar el agrupamiento)
            item_instancia = QTableWidgetItem(p.instancia)
            item_instancia.setFlags(item_instancia.flags() & ~Qt.ItemIsEditable)
            if p.instancia == "Final":
                item_instancia.setForeground(Qt.darkBlue)
            self.tabla_resultados.setItem(row, 2, item_instancia)
            
            # Resultado
            tiempo = p.resultado if p.resultado else "---"
            item_resultado = QTableWidgetItem(tiempo)
            item_resultado.setFlags(item_resultado.flags() & ~Qt.ItemIsEditable)
            self.tabla_resultados.setItem(row, 3, item_resultado)
            
            # --- POSICIÓN DINÁMICA POR BLOQUE ---
            item_pos = QTableWidgetItem(f"{pos_contador}" if p.resultado and p.resultado != "---" and p.resultado != "00:00.00" else "-")
            item_pos.setFlags(item_pos.flags() & ~Qt.ItemIsEditable)
            if p.resultado and p.resultado != "---" and p.resultado != "00:00.00":
                pos_contador += 1
            self.tabla_resultados.setItem(row, 4, item_pos)

            # Botón Eliminar
            btn_eliminar = QPushButton("🗑")
            btn_eliminar.setFixedWidth(30)
            btn_eliminar.clicked.connect(lambda ch=False, pid=p.id_participacion: self.confirmar_eliminacion(pid))
            self.tabla_resultados.setCellWidget(row, 5, btn_eliminar)

        # Volver a conectar la señal al finalizar la carga
        self.tabla_resultados.itemChanged.connect(self.al_cambiar_item_tabla)

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
            self.input_cc.setText("00")
            self.cargar_participantes()
            self.input_dorsal.setFocus()

        else:
            QMessageBox.warning(
                self, 
                "Error de carga", 
                f"No se encontró al atleta con dorsal {dorsal_str} en la instancia '{instancia_carga}'."
            )

    def al_cambiar_item_tabla(self, item):
        if item.column() != 0:
            return
            
        id_participacion = item.data(Qt.UserRole)
        if id_participacion is None:
            return
            
        nuevo_dorsal_str = item.text().strip()
        
        if not nuevo_dorsal_str or nuevo_dorsal_str == "---":
            self.participacion_repo.actualizar_dorsal(id_participacion, None)
            self.cargar_participantes()
            return
            
        try:
            nuevo_dorsal = int(nuevo_dorsal_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "El dorsal debe ser un número entero.")
            self.cargar_participantes()
            return

        # Validar si el dorsal ya está ocupado por otro atleta en la prueba
        conn = self.participacion_repo.db.obtener_conexion()
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM PARTICIPA 
                WHERE id_prueba = ? AND numero_dorsal = ? AND id_participacion != ?
            """, (self.prueba.id_prueba, nuevo_dorsal, id_participacion))
            duplicados = cursor.fetchone()[0]

        if duplicados > 0:
            QMessageBox.warning(self, "Error", f"El dorsal {nuevo_dorsal} ya está siendo usado por otro atleta en esta prueba.")
            self.cargar_participantes()
            return

        self.participacion_repo.actualizar_dorsal(id_participacion, nuevo_dorsal)
        self.cargar_participantes()

    def confirmar_eliminacion(self, id_participacion):
        res = QMessageBox.question(self, "Confirmar", "¿Desea eliminar este atleta de la prueba?",
                                    QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            self.participacion_repo.eliminar_participacion(id_participacion)
            self.cargar_participantes()

    def abrir_editar_prueba(self):
        from ui.views.dialogs.nueva_prueba_dialog import NuevaPruebaDialog
        from database.repositories.prueba_repository import PruebaRepository
        prueba_repo = PruebaRepository(self.participacion_repo.db)
        
        dialog = NuevaPruebaDialog(self.prueba.id_torneo, prueba=self.prueba, parent=self)
        if dialog.exec() == QDialog.Accepted:
            try:
                prueba_repo.actualizar(dialog.prueba_creada)
                self.prueba = dialog.prueba_creada
                # Actualizar título de cabecera
                icon = "  ▼ " if self.is_expanded else "  ▶ "
                self.header_button.setText(f"{icon} {self.prueba.nombre} - {self.prueba.categoria} ({self.prueba.sexo})")
                self.cargar_participantes()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar la prueba:\n{str(e)}")
                 
    def confirmar_eliminacion_prueba(self):
        res = QMessageBox.warning(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar esta prueba?\n\n¡ADVERTENCIA! Se eliminarán todas las inscripciones y resultados cargados para esta prueba.",
            QMessageBox.Yes | QMessageBox.No
        )
        if res == QMessageBox.Yes:
            from database.repositories.prueba_repository import PruebaRepository
            prueba_repo = PruebaRepository(self.participacion_repo.db)
            try:
                prueba_repo.eliminar(self.prueba.id_prueba)
                # Recargar pruebas en TorneosView buscando en ancestros
                widget = self.parentWidget()
                while widget:
                    if hasattr(widget, "cargar_pruebas"):
                        widget.cargar_pruebas()
                        break
                    widget = widget.parentWidget()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar la prueba:\n{str(e)}")