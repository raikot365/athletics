## @file test_repositories.py
import sys
import os
# --- AGREGAR LA CARPETA 'src' AL PATH DE PYTHON ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from models.torneo import Torneo
from models.atleta import Atleta
from models.prueba import Prueba
from models.participacion import Participacion

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

def test_flujo_completo_atleta(repo_atleta):
    """Prueba la creación, actualización y eliminación de atletas."""
    # 1. Crear
    atleta = Atleta(None, "34567890", "Juan", "Perez", "1995-04-12", genero="M", id_localidad=1, provincia="Misiones", club="CEF N1")
    repo_atleta.crear(atleta)
    assert atleta.id_atleta is not None
    assert atleta.genero == "M"

    # 2. Buscar/Filtrar
    encontrados = repo_atleta.buscar_filtrado("Perez")
    assert len(encontrados) == 1
    assert encontrados[0].nombre == "Juan"
    assert encontrados[0].genero == "M"

    # 3. Actualizar
    atleta.nombre = "Juan Carlos"
    atleta.genero = "M"
    repo_atleta.actualizar(atleta)
    
    encontrados_act = repo_atleta.buscar_filtrado("Juan Carlos")
    assert len(encontrados_act) == 1
    assert encontrados_act[0].nombre == "Juan Carlos"
    assert encontrados_act[0].genero == "M"

    # 4. Eliminar
    repo_atleta.eliminar(atleta.id_atleta)
    encontrados_elim = repo_atleta.buscar_filtrado("Juan Carlos")
    assert len(encontrados_elim) == 0

def test_buscar_para_inscripcion_filtro_genero(repo_atleta, repo_prueba, repo_torneo):
    """Prueba que la búsqueda de atletas para inscripción filtre adecuadamente por género."""
    # 1. Crear atletas masculino y femenino
    atleta_m = Atleta(None, "11111111", "Luis", "Gomez", "2000-01-01", genero="M", id_localidad=1)
    atleta_f = Atleta(None, "22222222", "Ana", "Gomez", "2002-02-02", genero="F", id_localidad=1)
    repo_atleta.crear(atleta_m)
    repo_atleta.crear(atleta_f)

    # 2. Crear torneo y prueba masculina
    torneo = repo_torneo.crear(Torneo(None, "Torneo Test", 1, "2026-05-20"))
    prueba_m = repo_prueba.crear(Prueba(None, "100m Llanos", "U20", "M", torneo.id_torneo))
    prueba_f = repo_prueba.crear(Prueba(None, "100m Llanos", "U20", "F", torneo.id_torneo))
    prueba_x = repo_prueba.crear(Prueba(None, "100m Llanos", "U20", "X", torneo.id_torneo))

    # 3. Buscar para prueba masculina
    res_m = repo_atleta.buscar_para_inscripcion("Gomez", prueba_m.id_prueba, "Final")
    assert len(res_m) == 1
    assert res_m[0]["nombre"] == "Luis"

    # 4. Buscar para prueba femenina
    res_f = repo_atleta.buscar_para_inscripcion("Gomez", prueba_f.id_prueba, "Final")
    assert len(res_f) == 1
    assert res_f[0]["nombre"] == "Ana"

    # 5. Buscar para prueba mixta (X)
    res_x = repo_atleta.buscar_para_inscripcion("Gomez", prueba_x.id_prueba, "Final")
    assert len(res_x) == 2

def test_dorsal_opcional_y_actualizar(repo_atleta, repo_prueba, repo_torneo, repo_participacion):
    """Prueba la inscripción con dorsal opcional (None), la validación de duplicados y la actualización."""
    # 1. Crear atletas
    atleta_1 = Atleta(None, "111", "Pedro", "Lopez", "2000-01-01", genero="M")
    atleta_2 = Atleta(None, "222", "Maria", "Lopez", "2002-02-02", genero="F")
    repo_atleta.crear(atleta_1)
    repo_atleta.crear(atleta_2)

    # 2. Crear torneo y prueba
    torneo = repo_torneo.crear(Torneo(None, "Torneo Test", 1, "2026-05-20"))
    prueba = repo_prueba.crear(Prueba(None, "Salto", "U20", "X", torneo.id_torneo))

    # 3. Inscribir con dorsal None
    p1 = Participacion(None, atleta_1.id_atleta, prueba.id_prueba, "Final", None, None)
    exito1 = repo_participacion.inscribir_atleta(p1)
    assert exito1 is True

    # 4. Validar disponibilidad de dorsal None (debe ser siempre True)
    assert repo_participacion.validar_dorsal_disponible(prueba.id_prueba, None) is True

    # 5. Inscribir atleta 2 con dorsal None (debe permitirse sin conflicto)
    p2 = Participacion(None, atleta_2.id_atleta, prueba.id_prueba, "Final", None, None)
    exito2 = repo_participacion.inscribir_atleta(p2)
    assert exito2 is True

    # 6. Actualizar dorsal de atleta 1 a un número y validar
    resultados = repo_participacion.obtener_resultados_prueba(prueba.id_prueba, "Final")
    id_part_1 = [r for r in resultados if r.nombre == "Pedro"][0].id_participacion
    id_part_2 = [r for r in resultados if r.nombre == "Maria"][0].id_participacion

    repo_participacion.actualizar_dorsal(id_part_1, 45)
    
    # 7. Validar disponibilidad
    assert repo_participacion.validar_dorsal_disponible(prueba.id_prueba, 45) is False
    assert repo_participacion.validar_dorsal_disponible(prueba.id_prueba, 99) is True

    # 8. Intentar liberar el dorsal (volver a None)
    repo_participacion.actualizar_dorsal(id_part_1, None)
    assert repo_participacion.validar_dorsal_disponible(prueba.id_prueba, 45) is True

def test_actualizar_y_eliminar_torneo_en_cascada(repo_torneo, repo_prueba, repo_participacion, repo_atleta):
    """Prueba que la actualización y eliminación de un torneo limpie en cascada sus pruebas y participaciones."""
    # 1. Crear torneo, prueba y participación
    torneo = repo_torneo.crear(Torneo(None, "Torneo Casc", 1, "2026-05-20"))
    prueba = repo_prueba.crear(Prueba(None, "100m", "U20", "M", torneo.id_torneo))
    atleta = Atleta(None, "999", "B", "A", "2000-01-01", genero="M")
    repo_atleta.crear(atleta)
    p = Participacion(None, atleta.id_atleta, prueba.id_prueba, "Final", 10, None)
    repo_participacion.inscribir_atleta(p)

    # 2. Actualizar torneo
    torneo.nombre = "Torneo Casc Act"
    repo_torneo.actualizar(torneo)
    recup = repo_torneo.obtener_por_id(torneo.id_torneo)
    assert recup.nombre == "Torneo Casc Act"

    # 3. Eliminar torneo en cascada
    repo_torneo.eliminar(torneo.id_torneo)

    # 4. Verificar eliminación total
    assert repo_torneo.obtener_por_id(torneo.id_torneo) is None
    assert len(repo_prueba.obtener_por_torneo(torneo.id_torneo)) == 0
    assert len(repo_participacion.obtener_resultados_prueba(prueba.id_prueba)) == 0

def test_actualizar_y_eliminar_prueba_en_cascada(repo_torneo, repo_prueba, repo_participacion, repo_atleta):
    """Prueba que la actualización y la eliminación de una prueba limpie sus participaciones."""
    # 1. Crear torneo, prueba y participación
    torneo = repo_torneo.crear(Torneo(None, "Torneo Casc P", 1, "2026-05-20"))
    prueba = repo_prueba.crear(Prueba(None, "100m P", "U20", "M", torneo.id_torneo))
    atleta = Atleta(None, "888", "D", "C", "2000-01-01", genero="M")
    repo_atleta.crear(atleta)
    p = Participacion(None, atleta.id_atleta, prueba.id_prueba, "Final", 12, None)
    repo_participacion.inscribir_atleta(p)

    # 2. Actualizar prueba
    prueba.nombre = "100m P Act"
    repo_prueba.actualizar(prueba)
    
    # Obtener todas las pruebas del torneo
    pruebas = repo_prueba.obtener_por_torneo(torneo.id_torneo)
    assert len(pruebas) == 1
    assert pruebas[0].nombre == "100m P Act"

    # 3. Eliminar prueba en cascada
    repo_prueba.eliminar(prueba.id_prueba)

    # 4. Verificar eliminación
    pruebas_elim = repo_prueba.obtener_por_torneo(torneo.id_torneo)
    assert len(pruebas_elim) == 0
    assert len(repo_participacion.obtener_resultados_prueba(prueba.id_prueba)) == 0