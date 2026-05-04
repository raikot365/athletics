## @file conftest.py
import sys
import os
import pytest

# Agregamos la carpeta 'src' al path para que los tests encuentren los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from database.database_manager import DatabaseManager
from database.repositories.torneo_repository import TorneoRepository
from database.repositories.participacion_repository import ParticipacionRepository

@pytest.fixture
def db_manager():
    """Configura una base de datos limpia en memoria para cada test."""
    db = DatabaseManager()
    db.db_path = ":memory:" # Usamos RAM para que sea ultra rápido y no deje basura
    db.inicializar_base_de_datos()
    return db

@pytest.fixture
def repo_torneo(db_manager):
    return TorneoRepository(db_manager)

@pytest.fixture
def repo_participacion(db_manager):
    return ParticipacionRepository(db_manager)