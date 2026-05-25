## @file prueba_repository.py
import sqlite3
from models.prueba import Prueba

class PruebaRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def obtener_por_torneo(self, id_torneo):
        query = "SELECT * FROM PRUEBA WHERE id_torneo = ?"
        with self.db.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id_torneo,))
            return [Prueba(**dict(row)) for row in cursor.fetchall()]
    
    def crear(self, prueba: Prueba):
        query = """INSERT INTO PRUEBA (nombre, categoria, sexo, id_torneo) 
                   VALUES (?, ?, ?, ?)"""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (prueba.nombre, prueba.categoria, prueba.sexo, prueba.id_torneo))
            prueba.id_prueba = cursor.lastrowid
            conn.commit()
            return prueba

    def actualizar(self, prueba: Prueba):
        query = """UPDATE PRUEBA 
                   SET nombre = ?, categoria = ?, sexo = ? 
                   WHERE id_prueba = ?"""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (prueba.nombre, prueba.categoria, prueba.sexo, prueba.id_prueba))
            conn.commit()

    def eliminar(self, id_prueba: int):
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            # 1. Eliminar participaciones asociadas a la prueba
            cursor.execute("DELETE FROM PARTICIPA WHERE id_prueba = ?", (id_prueba,))
            # 2. Eliminar la prueba
            cursor.execute("DELETE FROM PRUEBA WHERE id_prueba = ?", (id_prueba,))
            conn.commit()