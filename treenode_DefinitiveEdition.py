class TreeNode:
    def __init__(self, tamano):
        self.proceso = None         # Nombre del proceso asignado
        self.ocupado = False        # Si el bloque está en uso
        self.tamano = tamano      # Tamaño del bloque (potencia de 2)
        self.tamOcupado = 0         # Tamaño real solicitado (para fragmentación interna)
        self.padre = None   
        self.hijoIzquierdo = None            
        self.hijoDerecho = None          


    def __repr__(self):
        return f"<TreeNode size={self.tamano}, ocupado={self.ocupado}, proceso={self.proceso}>"


class BuddySystem:
    def __init__(self, tamano=1024):
        self.total = self.get_required_block_size(tamano)
        self.root = TreeNode(self.total)

    @staticmethod
    def get_required_block_size(size):
        """Calcula la menor potencia de 2 >= size"""
        power_of_2 = 1
        while power_of_2 < size:
            power_of_2 *= 2
        return power_of_2

    def _split(self, node: TreeNode):
        """Divide un bloque en dos buddies"""
        mitad = node.tamano // 2
        node.hijoIzquierdo = TreeNode(mitad)
        node.hijoDerecho = TreeNode(mitad)
        node.hijoIzquierdo.padre = node
        node.hijoDerecho.padre = node

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
            print(f"✅ Proceso {proceso} asignado en bloque de {nodo.tamano}")
        else:
            print("❌ No se encontró bloque disponible")

    def _allocate(self, node: TreeNode, espacio2: int):
        """Busca un bloque libre del tamaño adecuado"""
        if node.ocupado:
            return None
        if node.tamano == espacio2 and not node.hijoIzquierdo:
            return node
        if node.tamano > espacio2:
            if not node.hijoIzquierdo:  # dividir si no tiene hijos
                self._split(node)
            return self._allocate(node.hijoIzquierdo, espacio2) or self._allocate(node.hijoDerecho, espacio2)
        return None

    def liberarMemoria(self, proceso: str):
        """Libera un bloque de memoria asignado a un proceso"""
        nodo = self._buscarNodo(self.root, proceso)
        if not nodo:
            print(f"⚠️ Proceso {proceso} no encontrado")
            return

        print(f"\n♻️ Liberando proceso {proceso} del bloque de {nodo.tamano}")
        nodo.ocupado = False
        nodo.proceso = None
        nodo.tamOcupado = 0
        self._merge(nodo)

    def _buscarNodo(self, node: TreeNode, proceso: str):
        if not node:
            return None
        if node.proceso == proceso:
            return node
        return self._buscarNodo(node.hijoIzquierdo, proceso) or self._buscarNodo(node.hijoDerecho, proceso)

    def _merge(self, node: TreeNode):
        """Fusiona buddies libres"""
        padre = node.padre
        if padre and padre.hijoIzquierdo and padre.hijoDerecho:
            if not padre.hijoIzquierdo.ocupado and not padre.hijoDerecho.ocupado and not padre.hijoIzquierdo.hijoIzquierdo and not padre.hijoDerecho.hijoDerecho:
                padre.hijoIzquierdo = None
                padre.hijoDerecho = None
                padre.ocupado = False
                self._merge(padre)

    def memoriaDesperdiciada(self, node: TreeNode = None):
        """Calcula fragmentación interna"""
        if node is None:
            node = self.root
        desperdicio = 0
        if node.ocupado:
            desperdicio += (node.tamano - node.tamOcupado)
        if node.hijoIzquierdo:
            desperdicio += self.memoriaDesperdiciada(node.hijoIzquierdo)
        if node.hijoDerecho:
            desperdicio += self.memoriaDesperdiciada(node.hijoDerecho)
        return desperdicio

    def mostrar(self, node: TreeNode = None, nivel=0):
        """Imprime el árbol de memoria (inorder jerárquico)"""
        if node is None:
            node = self.root
        if node:
            print("  " * nivel + f"[{node.tamano}] {'Ocupado' if node.ocupado else 'Libre'} - {node.proceso}")
            if node.hijoIzquierdo: 
                self.mostrar(node.hijoIzquierdo, nivel + 1)
            if node.hijoDerecho:
                self.mostrar(node.hijoDerecho, nivel + 1)


# Ejemplo de uso
if __name__ == "__main__":
    memoria = BuddySystem(1024)

    memoria.asignarMemoria(200, "A")
    memoria.mostrar()
    memoria.asignarMemoria(200, "B")
    memoria.mostrar()

    memoria.asignarMemoria(200, "C")
    memoria.mostrar()
    
    memoria.asignarMemoria(200, "D")
    memoria.mostrar()
    
    memoria.liberarMemoria("A")
    memoria.mostrar()

    memoria.liberarMemoria("B")
    memoria.mostrar()


    print("\nMemoria desperdiciada:", memoria.memoriaDesperdiciada())
