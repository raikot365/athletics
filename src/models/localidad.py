## @file localidad.py
#  @brief Representa una localidad geográfica.
from dataclasses import dataclass

@dataclass
class Localidad:
    """
    Clase de datos para las localidades.
    """
    id_localidad: int = None
    nombre: str = ""