## @file participacion_repository.py
#  @brief Gestiona las inscripciones y resultados.

from database.database_manager import DatabaseManager
import sqlite3
from models.participacion import Participacion
from models.atleta import Atleta

class ParticipacionRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    ## Registra un resultado buscando al atleta por su dorsal en esa prueba.

    def cargar_resultado_por_dorsal(self, id_prueba, numero_dorsal, instancia, tiempo):
        """
        Actualiza el tiempo de un atleta basado en su número de dorsal en una prueba específica.
        @return True si se actualizó correctamente, False si el dorsal no existe en la prueba.
        """
        query = """UPDATE PARTICIPA 
                   SET resultado = ? 
                   WHERE id_prueba = ? AND numero_dorsal = ? AND instancia = ?"""
        
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (tiempo, id_prueba, numero_dorsal, instancia))
            conn.commit()
            return cursor.rowcount > 0
            
    ## Obtiene los resultados de una prueba ordenados por tiempo.
    def obtener_resultados_prueba(self, id_prueba, instancia=None):
        """
        Obtiene los atletas inscritos en una prueba.
        Devuelve una lista de objetos que combinan datos de Participación y Atleta.
        """
        # Hacemos un JOIN para traer el apellido y nombre del atleta junto con sus resultados
        query = """
            SELECT p.id_participacion, p.id_atleta, p.instancia, 
                   p.numero_dorsal, p.resultado,
                   a.apellido, a.nombre, a.club
            FROM PARTICIPA p
            JOIN ATLETA a ON p.id_atleta = a.id_atleta
            WHERE p.id_prueba = ?
        """
        params = [id_prueba]
        
        if instancia:
            query += " AND p.instancia = ?"
            params.append(instancia)
            
        # ORDEN COMPUESTO: Primero por instancia, luego por tiempo (los nulos al final)
        query += " ORDER BY p.instancia ASC, p.resultado ASC NULLS LAST" 
        
        with self.db.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            resultados = []
            for row in cursor.fetchall():
                class Registro: pass
                r = Registro()
                r.id_participacion = row['id_participacion']
                r.numero_dorsal = row['numero_dorsal']
                r.apellido = row['apellido']
                r.nombre = row['nombre']
                r.instancia = row['instancia']
                r.club = row['club']
                r.resultado = row['resultado']
                resultados.append(r)
            return resultados
    
    ## Inscribe a un atleta en una prueba.
    #  @param participacion Objeto con id_atleta, id_prueba, instancia y dorsal.
    def inscribir_atleta(self, participacion: Participacion):
        query = """INSERT INTO PARTICIPA (id_atleta, id_prueba, instancia, numero_dorsal) 
                   VALUES (?, ?, ?, ?)"""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, (
                    participacion.id_atleta, 
                    participacion.id_prueba, 
                    participacion.instancia, 
                    participacion.numero_dorsal
                ))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # El atleta ya está inscrito en esta prueba/instancia
                return False

    ## Valida si un número de dorsal ya está siendo usado en una prueba específica.
    #  @return True si el dorsal está disponible.
    def validar_dorsal_disponible(self, id_prueba, numero_dorsal):
        if numero_dorsal is None:
            return True
        query = "SELECT COUNT(*) FROM PARTICIPA WHERE id_prueba = ? AND numero_dorsal = ?"
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_prueba, numero_dorsal))
            return cursor.fetchone()[0] == 0

    def actualizar_dorsal(self, id_participacion, numero_dorsal):
        """Actualiza el número de dorsal de una participación."""
        query = "UPDATE PARTICIPA SET numero_dorsal = ? WHERE id_participacion = ?"
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (numero_dorsal, id_participacion))
            conn.commit()

    ## Obtiene atletas que NO están inscritos en una prueba específica.
    #  Útil para el buscador de la interfaz de inscripción.
    def obtener_atletas_no_inscritos(self, id_prueba):
        query = """SELECT * FROM ATLETA 
                   WHERE id_atleta NOT IN (
                       SELECT id_atleta FROM PARTICIPA WHERE id_prueba = ?
                   )"""
        with self.db.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id_prueba,))
            return [Atleta(**dict(row)) for row in cursor.fetchall()]

    ## Elimina una inscripción (por si hubo un error antes de cargar resultados).
    def eliminar_inscripcion(self, id_participacion):
        query = "DELETE FROM PARTICIPA WHERE id_participacion = ?"
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_participacion,))
            conn.commit()

    def eliminar_participacion(self, id_participacion):
        """Elimina a un atleta de una prueba específica."""
        query = "DELETE FROM PARTICIPA WHERE id_participacion = ?"
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_participacion,))
            conn.commit()