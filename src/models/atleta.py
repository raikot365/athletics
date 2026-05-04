## @file atleta.py
#  @brief Representa a un atleta participante.
from dataclasses import asdict, dataclass
from datetime import date

@dataclass
class Atleta:
    """
    Clase que contiene la información personal y federativa del atleta.
    """
    id_atleta: int = None
    dni: str = ""
    nombre: str = ""
    apellido: str = ""
    fecha_nacimiento: date = None
    id_localidad: int = None
    provincia: str = "Misiones"
    club: str = ""

    ## Convierte la instancia en un diccionario.
    def to_dict(self):
        return asdict(self)

    ## Crea una instancia desde un diccionario.
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def nombre_completo(self) -> str:
        """
        Retorna el nombre y apellido formateado.
        @return String con 'Apellido, Nombre'.
        """
        return f"{self.apellido}, {self.nombre}"