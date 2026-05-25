## @file torneos_view.py
#  @brief Vista principal para la gestión de torneos y pruebas.

from ui.views.dialogs.nuevo_torneo_dialog import NuevoTorneoDialog
from ui.widgets.prueba_widget import PruebaWidget
from ui.views.dialogs.nueva_prueba_dialog import NuevaPruebaDialog
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QScrollArea, QFrame, QDialog, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt
from services.exporter import ExcelExporter

class TorneosView(QWidget):
    def __init__(self, torneo_repo, prueba_repo, atleta_repo, participacion_repo):
        super().__init__()
        self.repo = torneo_repo
        self.repo_prueba = prueba_repo
        self.repo_atleta = atleta_repo
        self.repo_participacion = participacion_repo
        self.torneo_seleccionado_id = None # Guardará el ID del torneo actual
        self.exporter = ExcelExporter(self.repo, self.repo_prueba, self.repo_participacion)
        self._setup_ui()
        self.cargar_torneos()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)

        # --- CABECERA Y CONTROLES ---
        self.header_layout = QHBoxLayout()
        titulo = QLabel("Gestión de Torneos")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        self.btn_nuevo_torneo = QPushButton("Nuevo Torneo")
        self.btn_nuevo_torneo.clicked.connect(self.abrir_dialogo_nuevo_torneo)
        self.btn_nuevo_torneo.setStyleSheet("background-color: #2980b9; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        
        self.header_layout.addWidget(titulo)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.btn_nuevo_torneo)
        self.layout.addLayout(self.header_layout)

        # --- TABLA DE TORNEOS ---
        self.tabla_torneos = QTableWidget(0, 4)
        self.tabla_torneos.setHorizontalHeaderLabels(["Nombre", "Edición", "Fecha", "Acciones"])
        
        header = self.tabla_torneos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)          # Nombre
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Edición
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Fecha 
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Acciones
        
        self.tabla_torneos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_torneos.setFixedHeight(150) # Ocupa poco espacio arriba
        self.tabla_torneos.itemSelectionChanged.connect(self.al_seleccionar_torneo)
        self.layout.addWidget(self.tabla_torneos)

        # --- CABECERA DE PRUEBAS ---
        self.header_pruebas_layout = QHBoxLayout()
        self.label_pruebas = QLabel("Seleccione un torneo para ver sus pruebas")
        self.label_pruebas.setStyleSheet("font-size: 16px; margin-top: 15px; font-weight: bold; color: #34495e;")
        
        # Botones de acción
        self.btn_reporte = QPushButton("📊 Exportar Excel")
        self.btn_reporte.setStyleSheet("background-color: #16a085; color: white; padding: 5px 15px; font-weight: bold; border-radius: 4px;")
        self.btn_reporte.setVisible(False)
        self.btn_reporte.clicked.connect(self.exportar_excel)

        self.btn_nueva_prueba = QPushButton("Nueva Prueba")
        self.btn_nueva_prueba.setStyleSheet("background-color: #e67e22; color: white; padding: 5px 15px; font-weight: bold; border-radius: 4px;")
        self.btn_nueva_prueba.setVisible(False)
        self.btn_nueva_prueba.clicked.connect(self.abrir_dialogo_nueva_prueba)
        
        # Agregamos al layout: Título -> Espacio -> Reporte -> Nueva Prueba
        self.header_pruebas_layout.addWidget(self.label_pruebas)
        self.header_pruebas_layout.addStretch() # Empuja todo lo que sigue a la derecha
        self.header_pruebas_layout.addWidget(self.btn_reporte)
        self.header_pruebas_layout.addSpacing(10) # Un pequeño aire entre botones
        self.header_pruebas_layout.addWidget(self.btn_nueva_prueba)

        self.btn_nueva_prueba.setVisible(False) # Oculto hasta que se seleccione un torneo
        self.layout.addLayout(self.header_pruebas_layout)

        # --- SCROLL AREA (Para los acordeones) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.scroll_content = QWidget()
        self.layout_pruebas = QVBoxLayout(self.scroll_content)
        self.layout_pruebas.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

    def cargar_torneos(self):
        """Lee los torneos de la BD y los pone en la tabla"""
        torneos = self.repo.obtener_todos()
        self.tabla_torneos.setRowCount(0)
        
        for row, torneo in enumerate(torneos):
            self.tabla_torneos.insertRow(row)
            item_nombre = QTableWidgetItem(torneo.nombre)
            item_nombre.setData(Qt.UserRole, torneo.id_torneo) 
            
            self.tabla_torneos.setItem(row, 0, item_nombre)
            self.tabla_torneos.setItem(row, 1, QTableWidgetItem(str(torneo.edicion)))
            self.tabla_torneos.setItem(row, 2, QTableWidgetItem(torneo.fecha_inicio))
            
            # Botones de Acciones
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setToolTip("Editar Torneo")
            btn_edit.setFixedWidth(30)
            btn_edit.clicked.connect(lambda checked=False, t=torneo: self.abrir_editar_torneo(t))
            
            btn_delete = QPushButton("🗑️")
            btn_delete.setToolTip("Eliminar Torneo")
            btn_delete.setFixedWidth(30)
            btn_delete.clicked.connect(lambda checked=False, tid=torneo.id_torneo: self.confirmar_eliminacion_torneo(tid))
            
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            actions_layout.addStretch()
            
            self.tabla_torneos.setCellWidget(row, 3, actions_widget)
    
    def abrir_dialogo_nuevo_torneo(self):
        """
        Muestra el formulario y, si el usuario acepta, guarda en BD y actualiza la tabla.
        """
        dialog = NuevoTorneoDialog(self.repo, self.repo_prueba, self.repo_atleta, self.repo_participacion)
        
        # dialog.exec() pausa la app hasta que la ventana se cierre
        if dialog.exec() == QDialog.Accepted: 
            nuevo_torneo = dialog.torneo_creado
            
            try:
                # Usar el repositorio para insertar en la BD
                self.repo.crear(nuevo_torneo)
                
                # Refrescar la tabla para mostrar el nuevo torneo
                self.cargar_torneos()
            except Exception as e:
                # Mostrar error si falla la BD
                QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo guardar:\n{str(e)}")

    def al_seleccionar_torneo(self):
        """Se dispara al hacer clic en una fila de la tabla."""
        selected_items = self.tabla_torneos.selectedItems()
        
        if not selected_items:
            return
            
        # Tomamos la fila seleccionada y sacamos el ID oculto
        fila = selected_items[0].row()
        item_nombre = self.tabla_torneos.item(fila, 0)
        if not item_nombre:
            return
            
        self.torneo_seleccionado_id = item_nombre.data(Qt.UserRole)
        
        # Actualizamos la UI
        self.label_pruebas.setText(f"Pruebas de: {item_nombre.text()}")
        self.btn_nueva_prueba.setVisible(True)
        
        # Cargamos las pruebas
        self.cargar_pruebas()
        self.btn_reporte.setVisible(True)
    
    def cargar_pruebas(self):
        """Busca las pruebas del torneo y dibuja los acordeones."""
        # 1. Limpiar el layout actual (por si había otro torneo seleccionado)
        while self.layout_pruebas.count():
            item = self.layout_pruebas.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 2. Buscar en base de datos
        pruebas = self.repo_prueba.obtener_por_torneo(self.torneo_seleccionado_id)

        # 3. Dibujar los widgets
        if not pruebas:
            self.layout_pruebas.addWidget(QLabel("No hay pruebas registradas en este torneo."))
        else:
            for prueba in pruebas:
                widget_acordeon = PruebaWidget(prueba, 
                    self.repo_atleta, 
                    self.repo_participacion)
                self.layout_pruebas.addWidget(widget_acordeon)
    
    def abrir_dialogo_nueva_prueba(self):
        # Asegurarnos de que hay un torneo seleccionado (por seguridad)
        if not self.torneo_seleccionado_id:
            return

        # Pasamos el ID del torneo al diálogo
        dialog = NuevaPruebaDialog(self.torneo_seleccionado_id, parent=self)

        if dialog.exec() == QDialog.Accepted:
            nueva_prueba = dialog.prueba_creada
            try:
                # Guardar en base de datos
                self.repo_prueba.crear(nueva_prueba)

                # Volver a cargar la lista de acordeones de este torneo
                self.cargar_pruebas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear la prueba:\n{str(e)}")

    def exportar_excel(self):
        if not self.torneo_seleccionado_id: return
        
        nombre_sugerido = f"Reporte_{self.label_pruebas.text().replace('Pruebas de: ', '')}.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte", nombre_sugerido, "Excel Files (*.xlsx)")
        
        if path:
            try:
                self.exporter.generar_reporte_torneo(self.torneo_seleccionado_id, path)
                QMessageBox.information(self, "Éxito", "Reporte generado correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo generar el Excel:\n{str(e)}")

    def abrir_editar_torneo(self, torneo):
        dialog = NuevoTorneoDialog(
            self.repo, self.repo_prueba, self.repo_atleta, self.repo_participacion, 
            torneo=torneo, parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            try:
                self.repo.actualizar(dialog.torneo_creado)
                self.cargar_torneos()
                if self.torneo_seleccionado_id == torneo.id_torneo:
                    self.label_pruebas.setText(f"Pruebas de: {dialog.torneo_creado.nombre}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el torneo:\n{str(e)}")

    def confirmar_eliminacion_torneo(self, id_torneo):
        res = QMessageBox.warning(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar este torneo?\n\n¡ADVERTENCIA! Se eliminarán en cascada todas sus pruebas, inscripciones y marcas/tiempos asociados de forma permanente.",
            QMessageBox.Yes | QMessageBox.No
        )
        if res == QMessageBox.Yes:
            try:
                self.repo.eliminar(id_torneo)
                if self.torneo_seleccionado_id == id_torneo:
                    self.torneo_seleccionado_id = None
                    self.label_pruebas.setText("Seleccione un torneo para ver sus pruebas")
                    self.btn_nueva_prueba.setVisible(False)
                    self.btn_reporte.setVisible(False)
                    # Limpiar el layout de pruebas
                    while self.layout_pruebas.count():
                        item = self.layout_pruebas.takeAt(0)
                        widget = item.widget()
                        if widget:
                            widget.deleteLater()
                self.cargar_torneos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el torneo:\n{str(e)}")