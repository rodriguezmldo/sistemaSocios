
class TreeNode:
    def __init__(self, tamanio: int):
        self.father = None        # Nodo superior (tamaño *2)
        self.left = None          # Nodo izquierdo (tamaño/2)
        self.right = None         # Nodo derecho (tamaño/2)
        self.tamanio = tamanio    # Tamaño, siempre potencia de 2
        self.visto = False        # Si este fragmento es visible
        self.ocupado = False      # Si está ocupado
        self.disponible = tamanio # Espacio disponible (inicialmente igual al tamaño)
        self.accesible = True     # Si puede ser ocupado
        self.proceso = " "        # Proceso asignado
        self.representacion = None # Panel o widget gráfico (si se usa en GUI)
        self.coordenada = 0       # Coordenada donde inicia
        self.tamOcupado = 0       # Tamaño ocupado
        self.etiqueta = None      # Etiqueta (si se usa en GUI)

    def __repr__(self):
        return f"<TreeNode size={self.tamanio}, ocupado={self.ocupado}, proceso='{self.proceso}'>"
