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
    
    def get_nombre(self, localidad_id):
        """Retorna el nombre de la localidad dado su ID."""
        query = "SELECT nombre FROM LOCALIDAD WHERE id_localidad = ?"
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (localidad_id,))
            result = cursor.fetchone()
            return result[0] if result else "Desconocida"