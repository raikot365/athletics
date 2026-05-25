## @file conftest.py
import sys
import os
import pytest

# Agregamos la carpeta 'src' al path para que los tests encuentren los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from database.database_manager import DatabaseManager
from database.repositories.torneo_repository import TorneoRepository
from database.repositories.participacion_repository import ParticipacionRepository
from database.repositories.atleta_repository import AtletaRepository
from database.repositories.prueba_repository import PruebaRepository

@pytest.fixture
def db_manager():
    """Configura una base de datos limpia para cada test."""
    db_file = "test_atletismo.db"
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except OSError:
            pass
            
    db = DatabaseManager(db_file)
    db.inicializar_base_de_datos()
    
    yield db
    
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except OSError:
            pass

@pytest.fixture
def repo_torneo(db_manager):
    return TorneoRepository(db_manager)

@pytest.fixture
def repo_participacion(db_manager):
    return ParticipacionRepository(db_manager)

@pytest.fixture
def repo_atleta(db_manager):
    return AtletaRepository(db_manager)

@pytest.fixture
def repo_prueba(db_manager):
    return PruebaRepository(db_manager)