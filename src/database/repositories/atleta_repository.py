## @file atleta_repository.py
#  @brief Repositorio para la gestión de datos de atletas.

import sqlite3
from database.database_manager import DatabaseManager
from models.atleta import Atleta

class AtletaRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    ## Agrega un nuevo atleta a la base de datos.
    def crear(self, atleta: Atleta):
        query = """INSERT INTO ATLETA (dni, nombre, apellido, fecha_nacimiento, genero, id_localidad, provincia, club) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (atleta.dni, atleta.nombre, atleta.apellido, 
                                 atleta.fecha_nacimiento, atleta.genero, atleta.id_localidad, 
                                 atleta.provincia, atleta.club))
            atleta.id_atleta = cursor.lastrowid
            conn.commit()

    ## Actualiza un atleta existente.
    def actualizar(self, atleta: Atleta):
        query = """UPDATE ATLETA 
                   SET dni = ?, nombre = ?, apellido = ?, fecha_nacimiento = ?, 
                       genero = ?, id_localidad = ?, provincia = ?, club = ?
                   WHERE id_atleta = ?"""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (atleta.dni, atleta.nombre, atleta.apellido, 
                                 atleta.fecha_nacimiento, atleta.genero, atleta.id_localidad, 
                                 atleta.provincia, atleta.club, atleta.id_atleta))
            conn.commit()

    ## Elimina un atleta y todas sus participaciones.
    def eliminar(self, id_atleta: int):
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM PARTICIPA WHERE id_atleta = ?", (id_atleta,))
            cursor.execute("DELETE FROM ATLETA WHERE id_atleta = ?", (id_atleta,))
            conn.commit()

    ## Busca atletas aplicando un filtro de texto (DNI, Nombre o Apellido).
    def buscar_filtrado(self, texto: str):
        query = """SELECT * FROM ATLETA 
                   WHERE dni LIKE ? OR nombre LIKE ? OR apellido LIKE ?"""
        filtro = f"%{texto}%"
        with self.db.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row # Permite acceder por nombre de columna
            cursor = conn.cursor()
            cursor.execute(query, (filtro, filtro, filtro))
            return [Atleta(**dict(row)) for row in cursor.fetchall()]

    def buscar_para_inscripcion(self, texto: str, id_prueba: int, instancia: str):
        """Busca atletas por DNI, Nombre o Apellido para el selector. Filtra por género de la prueba y excluye ya inscritos."""
        # 1. Obtener el sexo de la prueba
        sexo_prueba = 'X'
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sexo FROM PRUEBA WHERE id_prueba = ?", (id_prueba,))
            row = cursor.fetchone()
            if row:
                sexo_prueba = row[0]

        # 2. Filtrar por género si es M o F
        query = """
            SELECT id_atleta, dni, nombre, apellido FROM ATLETA 
            WHERE (dni LIKE ? OR nombre LIKE ? OR apellido LIKE ?)
        """
        params = [f"%{texto}%", f"%{texto}%", f"%{texto}%"]

        if sexo_prueba in ('M', 'F'):
            query += " AND genero = ?"
            params.append(sexo_prueba)

        query += """
            AND id_atleta NOT IN (
                SELECT id_atleta FROM PARTICIPA 
                WHERE id_prueba = ? AND instancia = ?
            )
            LIMIT 10
        """
        params.extend([id_prueba, instancia])

        with self.db.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()