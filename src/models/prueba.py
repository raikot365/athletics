## @file prueba.py
#  @brief Representa una disciplina dentro de un torneo.
from dataclasses import dataclass

@dataclass
class Prueba:
    """
    Representa una prueba específica (ej: 100m llanos, Salto en largo).
    """
    id_prueba: int = None
    nombre: str = ""
    categoria: str = ""  # U18, U20, Mayores, etc.
    sexo: str = "X"      # M, F o X
    id_torneo: int = None