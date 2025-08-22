class proceso:
    def __init__(self, nombre, tamano):
        self.nombre = nombre
        self.tamano = tamano

    def asignarMemoria(self, espacio: int, proceso: str):
        """Asigna memoria a un proceso usando buddy system"""
        print(f"\n➡️ Proceso {proceso} solicita {espacio} unidades")
        
        espacio2 = self.get_required_block_size(espacio)

        if espacio2 > self.total:
            print("❌ No hay suficiente memoria total")
            return None

        nodo = self._allocate(self.root, espacio2)
        if nodo:
            nodo.ocupado = True
            nodo.proceso = proceso
            nodo.tamOcupado = espacio
            print(f"✅ Proceso {proceso} asignado en bloque de {nodo.tamanio}")
        else:
            print("❌ No se encontró bloque disponible")
        
    def liberarMemoria(self, proceso: str):
        """Libera un bloque de memoria asignado a un proceso"""
        nodo = self._buscarNodo(self.root, proceso)
        if not nodo:
            print(f"⚠️ Proceso {proceso} no encontrado")
            return

        print(f"\n♻️ Liberando proceso {proceso} del bloque de {nodo.tamanio}")
        nodo.ocupado = False
        nodo.proceso = None
        nodo.tamOcupado = 0
        self._merge(nodo)