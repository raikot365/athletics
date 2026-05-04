## @file database_manager.py
#  @brief Gestión de la base de datos SQLite para la App de Atletismo.

import sqlite3
import os

class DatabaseManager:
    """
    Clase responsable de la conexión, creación de tablas e inicialización de datos.
    """

    def __init__(self, db_name="atletismo.db"):
        ## Ruta del archivo de base de datos.
        self.db_name = db_name

    def obtener_conexion(self):
        """
        Establece una conexión con la base de datos.
        @return Objeto connection de sqlite3.
        """
        return sqlite3.connect(self.db_name)

    def inicializar_base_de_datos(self):
        """
        Crea las tablas necesarias y puebla la tabla de localidades.
        """
        with self.obtener_conexion() as conn:
            cursor = conn.cursor()

            # Habilitar claves foráneas en SQLite
            cursor.execute("PRAGMA foreign_keys = ON;")

            # 1. Tabla Localidad
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS LOCALIDAD (
                    id_localidad INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL
                )
            ''')

            # 2. Tabla Atleta
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ATLETA (
                    id_atleta INTEGER PRIMARY KEY AUTOINCREMENT,
                    dni TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    fecha_nacimiento TEXT NOT NULL,
                    id_localidad INTEGER,
                    provincia TEXT DEFAULT 'Misiones',
                    club TEXT,
                    FOREIGN KEY (id_localidad) REFERENCES LOCALIDAD(id_localidad) ON DELETE SET NULL
                )
            ''')

            # 3. Tabla Torneo
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS TORNEO (
                    id_torneo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    edicion INTEGER,
                    fecha_inicio TEXT NOT NULL
                )
            ''')

            # 4. Tabla Prueba
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS PRUEBA (
                    id_prueba INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    categoria TEXT,
                    sexo TEXT CHECK(sexo IN ('M', 'F', 'X')),
                    id_torneo INTEGER NOT NULL,
                    FOREIGN KEY (id_torneo) REFERENCES TORNEO(id_torneo) ON DELETE CASCADE
                )
            ''')

            # 5. Tabla Participa
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS PARTICIPA (
                    id_participacion INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_atleta INTEGER NOT NULL,
                    id_prueba INTEGER NOT NULL,
                    instancia TEXT NOT NULL,
                    numero_dorsal INTEGER,
                    resultado TEXT,
                    FOREIGN KEY (id_atleta) REFERENCES ATLETA(id_atleta),
                    FOREIGN KEY (id_prueba) REFERENCES PRUEBA(id_prueba)
                )
            ''')

            # Poblar localidades si la tabla está vacía
            cursor.execute("SELECT COUNT(*) FROM LOCALIDAD")
            if cursor.fetchone()[0] == 0:
                self._poblar_localidades(cursor)
            
            conn.commit()
            print("Base de datos inicializada correctamente.")

    def _poblar_localidades(self, cursor):
        """
        Inserta la lista de localidades de Misiones.
        """
        # 1. Definimos una lista simple de strings (más fácil de leer y editar)
        nombres_localidades = [
            "9 de Julio", "25 de Mayo", "Alba Posse", "Almafuerte", "Apóstoles",
            "Aristóbulo del Valle", "Arroyo del Medio", "Azara", "Barra Concepción",
            "Barrio Bernardino Rivadavia", "Barrio del Lago", "Barrio Rural", "Bernardo de Irigoyen",
            "Bonpland","Caá Yarí",
            "Camión Cue",
            "Campo Grande",
            "Campo Ramón",
            "Campo Viera",
            "Candelaria",
            "Capioví",
            "Caraguatay",
            "Cerro Azul",
            "Cerro Corá",
            "Colonia Alberdi",
            "Colonia Alicia",
            "Colonia Aparecida",
            "Colonia Aurora",
            "Colonia Delicia",
            "Colonia Helvecia",
            "Colonia Polana",
            "Colonia Victoria",
            "Comandante Andresito",
            "Concepción de la Sierra",
            "Corpus Christi",
            "Cruce Caballero",
            "Domingo Savio",
            "Dos Arroyos",
            "Dos de Mayo",
            "Dos Hermanas",
            "El Alcázar",
            "El Piñalito",
            "El Soberbio",
            "Eldorado",
            "Estación Apóstoles",
            "Fachinal",
            "Florentino Ameghino",
            "Fracrán",
            "Garuhapé",
            "Garuhapé-Mi",
            "General Alvear",
            "General Urquiza",
            "Gobernador Lanusse",
            "Gobernador López",
            "Gobernador Roca",
            "Guaraní",
            "Hipólito Yrigoyen",
            "Integración",
            "Itacaruaré",
            "Jardín América",
            "La Corita",
            "Laharrague",
            "Leandro N. Alem",
            "Loreto",
            "Los Helechos",
            "Mártires",
            "Mbopicuá",
            "Mojón Grande",
            "Montecarlo",
            "Nemesio Parma",
            "Nueve de Julio Kilómetro 20",
            "Oasis",
            "Olegario Víctor Andrade",
            "Panambí",
            "Panambí Kilómetro 8",
            "Paraje Fontana",
            "Peñón del Teyú Cuaré",
            "Pindapoy",
            "Piray Kilómetro 18",
            "Pozo Azul",
            "Primero de Mayo",
            "Profundidad",
            "Pueblo Illia",
            "Pueblo Salto",
            "Puerto Azara",
            "Puerto Esperanza",
            "Puerto Iguazú",
            "Puerto Leoni",
            "Puerto Libertad",
            "Puerto Mado",
            "Puerto Mineral",
            "Puerto Pinares",
            "Puerto Piray",
            "Puerto Rico",
            "Puerto Santa Ana",
            "Reserva natural de la defensa Puerto Península",
            "Roca Chica",
            "Ruiz de Montoya",
            "Salto Encantado",
            "San Alberto",
            "San Antonio",
            "San Francisco de Asís",
            "San Gotardo",
            "San Ignacio",
            "San Javier",
            "San José",
            "San Martín",
            "San Pedro",
            "San Vicente",
            "Santa Ana",
            "Santa María",
            "Santa Rita",
            "Santiago de Liniers",
            "Santo Pipó",
            "Tarumá",
            "Terciados Paraíso",
            "Tobuna",
            "Torta Quemada",
            "Tres Capones",
            "Valle Hermoso",
            "Villa Akerman",
            "Villa Bonita",
            "Villa Libertad",
            "Villa Parodi",
            "Villa Roulet",
            "Villalonga",
            "Wanda"
        ]

        # 2. TRUCO: Convertimos cada string en una tupla de un solo elemento (nombre,)
        # Esto genera: [('9 de Julio',), ('25 de Mayo',), ...]
        datos_formateados = [(nombre,) for nombre in nombres_localidades]

        # 3. Ahora executemany recibirá correctamente una "lista de tuplas de 1 elemento"
        cursor.executemany("INSERT INTO LOCALIDAD (nombre) VALUES (?)", datos_formateados)