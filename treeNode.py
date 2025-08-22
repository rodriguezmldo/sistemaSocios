from process import *

class TreeNode:
    def __init__(self, tamanio):
        self.tamanio = tamanio      # Tamaño del bloque (potencia de 2)
        self.ocupado = False        # Si el bloque está en uso
        self.proceso = None         # Nombre del proceso asignado
        self.tamOcupado = 0         # Tamaño real solicitado (para fragmentación interna)
        self.left = None            # Hijo izquierdo (buddy)
        self.right = None           # Hijo derecho (buddy)
        self.father = None          # Padre en el árbol

    def __repr__(self):
        return f"<TreeNode size={self.tamanio}, ocupado={self.ocupado}, proceso={self.proceso}>"


class BuddySystem:
    def __init__(self, tamanio=1024):
        self.total = self.get_required_block_size(tamanio)
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
        mitad = node.tamanio // 2
        node.left = TreeNode(mitad)
        node.right = TreeNode(mitad)
        node.left.father = node
        node.right.father = node


    def _allocate(self, node: TreeNode, espacio2: int):
        """Busca un bloque libre del tamaño adecuado"""
        if node.ocupado:
            return None
        if node.tamanio == espacio2 and not node.left:
            return node
        if node.tamanio > espacio2:
            if not node.left:  # dividir si no tiene hijos
                self._split(node)
            return self._allocate(node.left, espacio2) or self._allocate(node.right, espacio2)
        return None


    def _buscarNodo(self, node: TreeNode, proceso: str):
        if not node:
            return None
        if node.proceso == proceso:
            return node
        return self._buscarNodo(node.left, proceso) or self._buscarNodo(node.right, proceso)

    def _merge(self, node: TreeNode):
        """Fusiona buddies libres"""
        padre = node.father
        if padre and padre.left and padre.right:
            if not padre.left.ocupado and not padre.right.ocupado and not padre.left.left and not padre.right.right:
                padre.left = None
                padre.right = None
                padre.ocupado = False
                self._merge(padre)
                
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

    def memoriaDesperdiciada(self, node: TreeNode = None):
        """Calcula fragmentación interna"""
        if node is None:
            node = self.root
        desperdicio = 0
        if node.ocupado:
            desperdicio += (node.tamanio - node.tamOcupado)
        if node.left:
            desperdicio += self.memoriaDesperdiciada(node.left)
        if node.right:
            desperdicio += self.memoriaDesperdiciada(node.right)
        return desperdicio

    def mostrar(self, node: TreeNode = None, nivel=0):
        """Imprime el árbol de memoria (inorder jerárquico)"""
        if node is None:
            node = self.root
        if node:
            print("  " * nivel + f"[{node.tamanio}] {'Ocupado' if node.ocupado else 'Libre'} - {node.proceso}")
            if node.left: 
                self.mostrar(node.left, nivel + 1)
            if node.right:
                self.mostrar(node.right, nivel + 1)


# Ejemplo de uso
if __name__ == "__main__":
    memoria = BuddySystem(1024)

    memoria.asignarMemoria(100, "A")
    memoria.asignarMemoria(200, "B")
    memoria.asignarMemoria(300, "C")

    memoria.mostrar()

    memoria.liberarMemoria("B")
    memoria.mostrar()

    print("\nMemoria desperdiciada:", memoria.memoriaDesperdiciada())

