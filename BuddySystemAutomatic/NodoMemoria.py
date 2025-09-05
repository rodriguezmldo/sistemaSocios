from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple

class NodoMemoria:
    def __init__(self, tamano: int, direccion: int = 0):
        # Cada nodo representa un bloque de memoria
        self.proceso: Optional[str] = None      # Nombre del proceso que ocupa este bloque
        self.ocupado: bool = False              # Indica si el bloque está en uso
        self.tamano: int = tamano               # Tamaño del bloque (potencia de 2)
        self.tamOcupado: int = 0                # Tamaño real solicitado (para calcular desperdicio)
        self.padre: Optional[NodoMemoria] = None
        self.hijoIzquierdo: Optional[NodoMemoria] = None
        self.hijoDerecho: Optional[NodoMemoria] = None
        self.direccion: int = direccion         # Dirección base del bloque (para identificar buddies)

    def es_hoja(self) -> bool:
        return self.hijoIzquierdo is None and self.hijoDerecho is None

    def __repr__(self):
        return f"<NodoMemoria tamano={self.tamano}, ocupado={self.ocupado}, proceso={self.proceso}, dir={self.direccion}>"