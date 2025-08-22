import math

class TreeNode:
    def __init__(self, tamanio):
        self.tamanio = tamanio
        self.disponible = tamanio
        self.left = None
        self.right = None
        self.father = None
        self.ocupado = False
        self.proceso = " "
        self.tamOcupado = 0
        self.accesible = True
        self.visto = True


class Tree:
    def __init__(self, tamanio=1024):
        self.root = TreeNode(tamanio)
        self.asignados = 0
        self.memoria = 0

    def crearArbol(self, x: TreeNode):
        """Divide un nodo en 2 subnodos (buddies)"""
        if x.tamanio >= 1:
            a = TreeNode(x.tamanio // 2)
            b = TreeNode(x.tamanio // 2)
            a.father = x
            b.father = x
            x.left = a
            x.right = b
            return a
        else:
            print("No se puede fragmentar más la memoria")
            return None

    def asignarMemoria(self, espacio: int, proceso: str):
        print(f"Tamaño solicitado: {espacio}")
        x = self.root
        bandera = False

        # Ajustar a potencia de 2
        log2 = math.ceil(math.log(espacio, 2))
        espacio2 = int(math.pow(2, log2))

        if espacio2 > self.root.disponible or espacio2 <= 0:
            print("No hay espacio disponible")
            return None

        while not bandera:
            if x.left is None or x.right is None:
                y = self.crearArbol(x)
                if y is None:
                    return None
            else:
                if espacio2 <= x.disponible and not x.left.ocupado:
                    y = x.left
                elif espacio2 <= x.disponible and not x.right.ocupado:
                    y = x.right
                elif x.father and espacio2 <= x.father.right.disponible and not x.father.right.ocupado:
                    y = x.father.right
                    x = x.father
                else:
                    print("No hay espacio adecuado")
                    return None

            # Condición de asignación
            if y.tamanio < espacio <= x.tamanio:
                x.father.accesible = False
                x.father.visto = False
                x.visto = True
                print(f"Se ocupa el bloque de {x.tamanio}")
                x.tamOcupado = espacio
                x.ocupado = True
                x.proceso = proceso

                # Actualizar disponibilidad hacia arriba
                z = x
                while z:
                    z.disponible -= x.tamanio
                    z = z.father

                x.accesible = False
                bandera = True
                return x
            else:
                x.accesible = False
                if x.right and x.right.tamanio == x.right.disponible:
                    x.right.visto = True
                if x.left and x.left.tamanio == x.left.disponible:
                    x.left.visto = True
                x.visto = False
                x = y

    def encontrarNodo(self, x: TreeNode, proceso: str):
        if x:
            if x.proceso == proceso:
                return x
            nodoIzq = self.encontrarNodo(x.left, proceso)
            if nodoIzq:
                return nodoIzq
            return self.encontrarNodo(x.right, proceso)
        return None

    def liberarMemoria(self, proceso: str):
        y = self.encontrarNodo(self.root, proceso)
        if not y:
            print("Proceso no encontrado")
            return

        print(f"Se liberó el proceso {y.proceso} de tamaño {y.tamanio}")
        y.ocupado = False
        y.proceso = " "
        y.tamOcupado = 0
        libera = y.tamanio

        while y:
            y.disponible += libera
            if (y.father and
                y.father.left.disponible == y.father.left.tamanio and
                y.father.right.disponible == y.father.right.tamanio):
                y.father.left.visto = False
                y.father.right.visto = False
                y.father.visto = True
                y.accesible = True
            y = y.father

    def memoriaDesperdiciada(self, x: TreeNode = None):
        if x is None:
            x = self.root
            self.memoria = 0
        if x:
            if x.proceso.strip() != "":
                self.memoria += (x.tamanio - x.tamOcupado)
            self.memoriaDesperdiciada(x.left)
            self.memoriaDesperdiciada(x.right)
        return self.memoria

    def inorder(self, x: TreeNode):
        if x:
            print("-------------------------------")
            print(f"Tamaño: {x.tamanio}, Disponible: {x.disponible}, Ocupado: {x.ocupado}, Proceso: {x.proceso}")
            self.inorder(x.left)
            self.inorder(x.right)


# Ejemplo de uso
if __name__ == "__main__":
    T = Tree(1024)
    T.asignarMemoria(100, "A")
    T.asignarMemoria(200, "B")
    T.inorder(T.root)
    T.liberarMemoria("A")
    print("Memoria desperdiciada:", T.memoriaDesperdiciada())
    T.inorder(T.root)
