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