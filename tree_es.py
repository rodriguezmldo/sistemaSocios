# Definición del nodo
class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.HijoIzquierdo = None
        self.HijoDerecho = None


# Árbol vacío al inicio
nodoRaiz = None


# Crear nuevo nodo
def nuevoNodo(elemento):
    return Nodo(elemento)


# Insertar un nodo
def insert(dato):
    global nodoRaiz
    tempNode = Nodo(dato)

    if nodoRaiz is None:
        nodoRaiz = tempNode
    else:
        actual = nodoRaiz
        padre = None
        while True:
            padre = actual
            if dato < padre.dato:
                actual = actual.HijoIzquierdo
                if actual is None:
                    padre.HijoIzquierdo = tempNode
                    return
            else:
                actual = actual.HijoDerecho
                if actual is None:
                    padre.HijoDerecho = tempNode
                    return


# Buscar un nodo
def search(dato):
    actual = nodoRaiz
    while actual is not None and actual.dato != dato:
        if dato < actual.dato:
            actual = actual.HijoIzquierdo
        else:
            actual = actual.HijoDerecho
    return actual


# Recorridos
def inorder(nodo):
    if nodo is not None:
        inorder(nodo.HijoIzquierdo)
        print(nodo.dato, end=" -> ")
        inorder(nodo.HijoDerecho)


def preorder(nodo):
    if nodo is not None:
        print(nodo.dato, end=" -> ")
        preorder(nodo.HijoIzquierdo)
        preorder(nodo.HijoDerecho)


def postorder(nodo):
    if nodo is not None:
        postorder(nodo.HijoIzquierdo)
        postorder(nodo.HijoDerecho)
        print(nodo.dato, end=" -> ")


# Programa principal
if __name__ == "__main__":
    insert(55)
    insert(20)
    insert(90)
    insert(50)
    insert(35)
    insert(15)
    insert(65)

    print("Insertion done ")
    print("\nPreorder Traversal: ")
    preorder(nodoRaiz)
    print("\nInorder Traversal: ")
    inorder(nodoRaiz)
    print("\nPostorder Traversal: ")
    postorder(nodoRaiz)

    ele = 35
    print(f"\n\nElement to be searched: {ele}")
    k = search(ele)
    if k is not None:
        print(f"Element {k.dato} found")
    else:
        print("Element not found")
