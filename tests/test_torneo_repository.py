# tests/test_torneo_repository.py
import pytest
import sqlite3
import sys
import os

# Aseguramos que pytest encuentre la carpeta src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from models.torneo import Torneo
from database.database_manager import DatabaseManager
from database.repositories.torneo_repository import TorneoRepository

@pytest.fixture
def repo_en_memoria():
    """Crea una base de datos temporal en memoria RAM para los tests."""
    # Instanciamos el manager pero forzamos la conexión a memoria
    db = DatabaseManager()
    db.db_path = ":memory:" 
    db.inicializar_base_datos()
    
    repo = TorneoRepository(db)
    yield repo
    # Al salir del test, la memoria se libera sola

def test_crear_y_obtener_torneo(repo_en_memoria):
    """Prueba que un torneo se guarde y recupere correctamente."""
    # 1. Preparar datos
    nuevo_torneo = Torneo(id_torneo=None, nombre="Nacional U20", edicion=2026, fecha_inicio="2026-10-15")
    
    # 2. Ejecutar acción
    torneo_creado = repo_en_memoria.crear(nuevo_torneo)
    
    # 3. Comprobar resultados (Asserts)
    assert torneo_creado.id_torneo is not None
    
    torneo_recuperado = repo_en_memoria.obtener_por_id(torneo_creado.id_torneo)
    assert torneo_recuperado.nombre == "Nacional U20"
    assert torneo_recuperado.edicion == 2026