## @file localidad_repository.py
import sqlite3
from models.localidad import Localidad

class LocalidadRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def obtener_todas(self):
        """Retorna todas las localidades de Misiones."""
        query = "SELECT * FROM LOCALIDAD ORDER BY nombre ASC"
        with self.db.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            return [Localidad(**dict(row)) for row in cursor.fetchall()]