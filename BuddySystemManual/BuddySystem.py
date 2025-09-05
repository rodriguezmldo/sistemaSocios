from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple
import hashlib
import math

from NodoMemoria import NodoMemoria
# =========================
#   LÓGICA DEL BUDDY SYSTEM
# =========================


class SistemaBuddy:
    def __init__(self, tamano_total: int = 1024, tam_min_bloque: int = 1):
        # Normaliza tamaño total a la potencia de 2 más cercana hacia arriba
        self.total = self.obtener_potencia_requerida(max(1, tamano_total))
        # Normaliza tamaño mínimo de bloque a la potencia de 2 más cercana hacia arriba
        self.min_bloque = self.obtener_potencia_requerida(max(1, tam_min_bloque))
        # Si el tamaño mínimo excede el total, se ajusta
        if self.min_bloque > self.total:
            self.min_bloque = self.total
        # Raíz del árbol de memoria
        self.raiz = NodoMemoria(self.total, 0)

    # =========================
    #   FUNCIONES AUXILIARES
    # =========================
    @staticmethod
    def es_potencia_de_2(x: int) -> bool:
        """Verifica si x es potencia de 2"""
        return x > 0 and (x & (x - 1)) == 0

    @staticmethod
    def obtener_potencia_requerida(tamano: int) -> int:
        """Devuelve la potencia de 2 más pequeña que sea >= tamaño"""
        potencia = 1
        while potencia < tamano:
            potencia <<= 1
        return potencia

    # =========================
    #   DIVISIÓN DE BLOQUES
    # =========================
    def _dividir(self, nodo: NodoMemoria):
        """Divide un bloque en dos buddies de la mitad del tamaño"""
        mitad = nodo.tamano // 2
        direccion_izq = nodo.direccion
        direccion_der = nodo.direccion + mitad
        
        # Se crean los hijos
        nodo.hijoIzquierdo = NodoMemoria(mitad, direccion_izq)
        nodo.hijoDerecho = NodoMemoria(mitad, direccion_der)
        nodo.hijoIzquierdo.padre = nodo
        nodo.hijoDerecho.padre = nodo

    # =========================
    #   ASIGNACIÓN DE MEMORIA
    # =========================
    def asignar_memoria(self, espacio: int, proceso: str) -> Optional[NodoMemoria]:
        """Solicita memoria para un proceso aplicando buddy system"""
        if not proceso:  # proceso vacío no es válido
            return None
        # Ajusta el espacio requerido a la potencia de 2 más cercana
        espacio2 = self.obtener_potencia_requerida(espacio)
        # Si excede el total disponible, no se puede asignar
        if espacio2 > self.total:
            return None
        # Busca nodo adecuado para asignar
        nodo = self._asignar(self.raiz, espacio2)
        if nodo:
            nodo.ocupado = True
            nodo.proceso = proceso
            nodo.tamOcupado = espacio  # espacio real solicitado (puede ser menor al asignado)
            return nodo
        return None

    def _asignar(self, nodo: NodoMemoria, espacio2: int) -> Optional[NodoMemoria]:
        """Recorre el árbol buscando un bloque libre adecuado para asignar"""
        # Si el nodo ya está ocupado, no sirve
        if nodo.ocupado:
            return None

        # Si tiene hijos, buscar recursivamente
        if not nodo.es_hoja():
            return self._asignar(nodo.hijoIzquierdo, espacio2) or self._asignar(nodo.hijoDerecho, espacio2)

        # Si es hoja:
        if nodo.tamano < espacio2:  # demasiado pequeño
            return None

        if nodo.tamano == espacio2:  # tamaño exacto
            return nodo

        # nodo más grande que lo solicitado → decidir si dividir o usar entero
        mitad = nodo.tamano // 2
        # Solo dividir si la mitad es >= espacio requerido y >= tamaño mínimo permitido
        if mitad >= max(espacio2, self.min_bloque):
            self._dividir(nodo)
            return self._asignar(nodo.hijoIzquierdo, espacio2) or self._asignar(nodo.hijoDerecho, espacio2)
        else:
            # No se puede dividir más → se asigna el bloque entero aunque sobre espacio
            return nodo

    # =========================
    #   LIBERACIÓN DE MEMORIA
    # =========================
    def liberar_memoria(self, proceso: str) -> bool:
        """Libera la memoria ocupada por un proceso"""
        nodo = self._buscar_nodo(self.raiz, proceso)
        if not nodo:
            return False
        # Marcar como libre
        nodo.ocupado = False
        nodo.proceso = None
        nodo.tamOcupado = 0
        # Intentar fusionar con su buddy
        self._fusionar(nodo)
        return True
    
    def _buscar_nodo(self, nodo: Optional[NodoMemoria], proceso: str) -> Optional[NodoMemoria]:
        """Busca el nodo asignado a un proceso"""
        if nodo is None:
            return None
        if nodo.proceso == proceso:
            return nodo
        # Buscar en hijos
        return self._buscar_nodo(nodo.hijoIzquierdo, proceso) or self._buscar_nodo(nodo.hijoDerecho, proceso)

    def _fusionar(self, nodo: NodoMemoria):
        """Fusiona nodos buddies si ambos están libres y son hojas"""
        padre = nodo.padre
        if padre and padre.hijoIzquierdo and padre.hijoDerecho:
            izq = padre.hijoIzquierdo
            der = padre.hijoDerecho
            # Se fusionan solo si ambos están libres y no han sido divididos
            if (not izq.ocupado and not der.ocupado and izq.es_hoja() and der.es_hoja()):
                padre.hijoIzquierdo = None
                padre.hijoDerecho = None
                padre.ocupado = False
                # Intentar fusionar hacia arriba
                self._fusionar(padre)

    # =========================
    #   MÉTRICAS DEL SISTEMA
    # =========================
    def memoria_desperdiciada(self, nodo: Optional[NodoMemoria] = None) -> int:
        """Calcula la cantidad de memoria desperdiciada en fragmentación interna"""
        if nodo is None:
            nodo = self.raiz
        desperdicio = 0
        if nodo.ocupado:
            # Bloque asignado pero con más tamaño que el usado
            desperdicio += (nodo.tamano - nodo.tamOcupado)
        # Recursión en hijos
        if nodo.hijoIzquierdo:
            desperdicio += self.memoria_desperdiciada(nodo.hijoIzquierdo)
        if nodo.hijoDerecho:
            desperdicio += self.memoria_desperdiciada(nodo.hijoDerecho)
        return desperdicio

    def procesos_vigentes(self) -> List[str]:
        """Devuelve la lista de procesos activos (sin repetidos, ordenados)"""
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
        """Calcula la dirección base del buddy de un bloque (XOR)"""
        return direccion ^ tamano
    
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
