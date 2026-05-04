## @file test_repositories.py
from models.torneo import Torneo

def test_flujo_completo_torneo(repo_torneo):
    """
    Prueba la creación, recuperación y listado de torneos.
    """
    # 1. Crear un torneo
    nuevo = Torneo(None, "Open Misiones 2026", "Edición Verano", "2026-02-10")
    creado = repo_torneo.crear(nuevo)
    
    # Verificaciones básicas
    assert creado.id_torneo is not None
    assert creado.nombre == "Open Misiones 2026"

    # 2. Obtener por ID
    recuperado = repo_torneo.obtener_por_id(creado.id_torneo)
    assert recuperado is not None
    assert recuperado.edicion == "Edición Verano"

    # 3. Listar todos
    todos = repo_torneo.obtener_todos()
    assert len(todos) >= 1
    assert any(t.nombre == "Open Misiones 2026" for t in todos)

def test_obtener_torneo_inexistente(repo_torneo):
    """Prueba que el repo maneje correctamente IDs que no existen."""
    resultado = repo_torneo.obtener_por_id(999)
    assert resultado is None