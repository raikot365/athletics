from src.database import DatabaseManager
from src.database.repositories.atleta_repository import AtletaRepository

def test_db_setup():
    db = DatabaseManager(":memory:") # Base de datos que desaparece al cerrar el test
    db.inicializar_base_de_datos()
    # Aquí verificas que las tablas existan...

def test_busqueda_atleta():
    # Usamos una DB en memoria para el test
    test_db = DatabaseManager(":memory:")
    test_db.inicializar_base_de_datos()
    
    repo = AtletaRepository(test_db)
    # Insertar un atleta de prueba...
    # Buscarlo...
    # assert resultado.nombre == "Nombre de prueba"