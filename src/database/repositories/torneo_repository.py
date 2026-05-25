## @file torneo_repository.py
#  @brief Repositorio para la gestión de Torneos.

from models.torneo import Torneo
import sqlite3

class TorneoRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def obtener_todos(self):
        query = "SELECT * FROM TORNEO ORDER BY fecha_inicio DESC"
        with self.db.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            return [Torneo(**dict(row)) for row in cursor.fetchall()]

    def crear(self, torneo: Torneo):
        query = "INSERT INTO TORNEO (nombre, edicion, fecha_inicio) VALUES (?, ?, ?)"
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (torneo.nombre, torneo.edicion, torneo.fecha_inicio))
            torneo.id_torneo = cursor.lastrowid
            conn.commit()
            return torneo
    
    def obtener_por_id(self, id_torneo):
        """Busca un torneo específico por su ID."""
        query = "SELECT * FROM TORNEO WHERE id_torneo = ?"
        with self.db.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id_torneo,))
            row = cursor.fetchone()
            
            if row:
                return Torneo(**dict(row))
            return None

    def actualizar(self, torneo: Torneo):
        query = "UPDATE TORNEO SET nombre = ?, edicion = ?, fecha_inicio = ? WHERE id_torneo = ?"
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (torneo.nombre, torneo.edicion, torneo.fecha_inicio, torneo.id_torneo))
            conn.commit()

    def eliminar(self, id_torneo: int):
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            # 1. Obtener las pruebas del torneo
            cursor.execute("SELECT id_prueba FROM PRUEBA WHERE id_torneo = ?", (id_torneo,))
            pruebas_ids = [row[0] for row in cursor.fetchall()]
            
            # 2. Eliminar participaciones asociadas
            if pruebas_ids:
                placeholders = ",".join("?" for _ in pruebas_ids)
                cursor.execute(f"DELETE FROM PARTICIPA WHERE id_prueba IN ({placeholders})", pruebas_ids)
                
            # 3. Eliminar pruebas
            cursor.execute("DELETE FROM PRUEBA WHERE id_torneo = ?", (id_torneo,))
            
            # 4. Eliminar torneo
            cursor.execute("DELETE FROM TORNEO WHERE id_torneo = ?", (id_torneo,))
            conn.commit()