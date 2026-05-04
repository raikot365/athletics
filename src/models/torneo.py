## @file torneo.py
#  @brief Representa un evento o competencia deportiva.
from dataclasses import dataclass
from datetime import date

@dataclass
class Torneo:
    """
    Define los datos básicos de un torneo de atletismo.
    """
    id_torneo: int = None
    nombre: str = ""
    edicion: int = 1
    fecha_inicio: date = None