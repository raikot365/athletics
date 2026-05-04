## @file participacion.py
#  @brief Relación entre Atleta y Prueba con sus resultados.
from dataclasses import dataclass

@dataclass
class Participacion:
    """
    Clase que vincula a un atleta con una prueba específica y registra su desempeño.
    """
    id_participacion: int = None
    id_atleta: int = None
    id_prueba: int = None
    instancia: str = "Final"  # Serie 1, Serie 2, Final, etc.
    numero_dorsal: int = None
    resultado: str = "00:00.00" # Tiempo o marca