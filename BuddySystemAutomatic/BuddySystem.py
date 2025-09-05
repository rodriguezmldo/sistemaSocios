from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple

from NodoMemoria import NodoMemoria

# =========================
#   LÓGICA DEL BUDDY SYSTEM
# =========================
class SistemaBuddy:
    def __init__(self, tamano_total: int = 1024, tam_min_bloque: int = 1):
        # Ajustes a potencias de 2
        self.total = self.obtener_potencia_requerida(max(1, tamano_total))
        self.min_bloque = self.obtener_potencia_requerida(max(1, tam_min_bloque))
        if self.min_bloque > self.total:
            # Corrige caso extremo
            self.min_bloque = self.total
        # Árbol raíz
        self.raiz = NodoMemoria(self.total, 0)

    @staticmethod
    def es_potencia_de_2(x: int) -> bool:
        return x > 0 and (x & (x - 1)) == 0

    @staticmethod
    def obtener_potencia_requerida(tamano: int) -> int:
        """Potencia de 2 más pequeña que sea >= tamaño"""
        potencia = 1
        while potencia < tamano:
            potencia <<= 1
        return potencia

    def _dividir(self, nodo: NodoMemoria):
        mitad = nodo.tamano // 2
        direccion_izq = nodo.direccion
        direccion_der = nodo.direccion + mitad
        
        nodo.hijoIzquierdo = NodoMemoria(mitad, direccion_izq)
        nodo.hijoDerecho = NodoMemoria(mitad, direccion_der)
        nodo.hijoIzquierdo.padre = nodo
        nodo.hijoDerecho.padre = nodo

    def asignar_memoria(self, espacio: int, proceso: str) -> Optional[NodoMemoria]:
        """Solicita memoria para un proceso aplicando buddy system"""
        if not proceso:
            return None
        espacio2 = self.obtener_potencia_requerida(espacio)
        if espacio2 > self.total:
            return None
        nodo = self._asignar(self.raiz, espacio2)
        if nodo:
            nodo.ocupado = True
            nodo.proceso = proceso
            nodo.tamOcupado = espacio
            return nodo
        return None

    def _asignar(self, nodo: NodoMemoria, espacio2: int) -> Optional[NodoMemoria]:
        # Si ocupado, no se puede usar
        if nodo.ocupado:
            return None

        # Si tiene hijos, intentar abajo
        if not nodo.es_hoja():
            return self._asignar(nodo.hijoIzquierdo, espacio2) or self._asignar(nodo.hijoDerecho, espacio2)

        # Es hoja libre
        if nodo.tamano < espacio2:
            return None

        if nodo.tamano == espacio2:
            return nodo

        # nodo.tamano > espacio2, decidir si dividir o asignar completo si no podemos dividir
        # Podemos dividir si la mitad es >= al máximo entre el espacio requerido y el tamaño mínimo de bloque
        mitad = nodo.tamano // 2
        if mitad >= max(espacio2, self.min_bloque):
            self._dividir(nodo)
            return self._asignar(nodo.hijoIzquierdo, espacio2) or self._asignar(nodo.hijoDerecho, espacio2)
        else:
            # No podemos dividir más por restricción de mínimo; asignar este bloque completo
            return nodo

    def liberar_memoria(self, proceso: str) -> bool:
        nodo = self._buscar_nodo(self.raiz, proceso)
        if not nodo:
            return False
        nodo.ocupado = False
        nodo.proceso = None
        nodo.tamOcupado = 0
        self._fusionar(nodo)
        return True

    def _buscar_nodo(self, nodo: Optional[NodoMemoria], proceso: str) -> Optional[NodoMemoria]:
        if nodo is None:
            return None
        if nodo.proceso == proceso:
            return nodo
        return self._buscar_nodo(nodo.hijoIzquierdo, proceso) or self._buscar_nodo(nodo.hijoDerecho, proceso)

    def _fusionar(self, nodo: NodoMemoria):
        padre = nodo.padre
        if padre and padre.hijoIzquierdo and padre.hijoDerecho:
            izq = padre.hijoIzquierdo
            der = padre.hijoDerecho
            # Fusionar sólo si ambos son hojas y libres
            if (not izq.ocupado and not der.ocupado and izq.es_hoja() and der.es_hoja()):
                padre.hijoIzquierdo = None
                padre.hijoDerecho = None
                padre.ocupado = False
                self._fusionar(padre)

    def memoria_desperdiciada(self, nodo: Optional[NodoMemoria] = None) -> int:
        if nodo is None:
            nodo = self.raiz
        desperdicio = 0
        if nodo.ocupado:
            desperdicio += (nodo.tamano - nodo.tamOcupado)
        if nodo.hijoIzquierdo:
            desperdicio += self.memoria_desperdiciada(nodo.hijoIzquierdo)
        if nodo.hijoDerecho:
            desperdicio += self.memoria_desperdiciada(nodo.hijoDerecho)
        return desperdicio

    # Utilidades para GUI
    def hojas_en_orden(self) -> List[NodoMemoria]:
        """Retorna la lista de bloques hoja de izquierda a derecha"""
        hojas: List[NodoMemoria] = []

        def _inorden(n: Optional[NodoMemoria]):
            if n is None:
                return
            if n.es_hoja():
                hojas.append(n)
            else:
                _inorden(n.hijoIzquierdo)
                _inorden(n.hijoDerecho)
        _inorden(self.raiz)
        return hojas

    def procesos_vigentes(self) -> List[str]:
        vistos = set()
        nombres: List[str] = []

        def _rec(n: Optional[NodoMemoria]):
            if n is None:
                return
            if n.ocupado and n.proceso and n.proceso not in vistos:
                vistos.add(n.proceso)
                nombres.append(n.proceso)
            _rec(n.hijoIzquierdo)
            _rec(n.hijoDerecho)
        _rec(self.raiz)
        return sorted(nombres)

    def obtener_buddy_address(self, direccion: int, tamano: int) -> int:
        """Calcula la dirección del buddy de un bloque"""
        # El buddy de un bloque está en la misma posición XOR el tamaño del bloque
        return direccion ^ tamano

    def memoria_ocupada(self, nodo: Optional[NodoMemoria] = None) -> int:
        if nodo is None:
            nodo = self.raiz
        ocupado = 0
        if nodo.ocupado:
            ocupado += nodo.tamOcupado  # sumar solo lo realmente usado
        if nodo.hijoIzquierdo:
            ocupado += self.memoria_ocupada(nodo.hijoIzquierdo)
        if nodo.hijoDerecho:
            ocupado += self.memoria_ocupada(nodo.hijoDerecho)
        return ocupado

    def memoria_disponible(self) -> int:
        return self.total - self.memoria_ocupada()