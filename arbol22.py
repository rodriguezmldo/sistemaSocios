class Block:
    def __init__(self, id, size, is_free=True):
        self.id = id
        self.size = size
        self.is_free = is_free
        self.children = []

    def __repr__(self):
        return f"Block(id={self.id}, size={self.size}KB, free={self.is_free})"


def get_required_block_size(size):
    """Calcula la menor potencia de 2 >= size."""
    power_of_2 = 1
    while power_of_2 < size:
        power_of_2 *= 2
    return power_of_2


def find_best_fit_block(node, required_size, best_fit=None):
    """
    Busca el bloque más pequeño en el árbol binario que cumpla el requisito.
    :param node: Nodo raíz o subárbol (Block).
    :param required_size: Tamaño mínimo necesario (potencia de 2).
    :param best_fit: Mejor bloque encontrado hasta ahora.
    """
    if node is None:
        return best_fit

    # Si es hoja (no tiene hijos)
    if not node.children:
        if node.is_free and node.size >= required_size:
            if best_fit is None or node.size < best_fit.size:
                best_fit = node

    # Si tiene hijos, buscamos recursivamente
    for child in node.children:
        best_fit = find_best_fit_block(child, required_size, best_fit)

    return best_fit


# --- Ejemplo de uso ---
if __name__ == "__main__":
    # Creamos un árbol de bloques de memoria
    root = Block(id=1, size=512, is_free=True)

    # Dividimos el bloque raíz en dos hijos de 256KB
    root.children = [
        Block(id=2, size=256, is_free=False),   # Ocupado
        Block(id=3, size=256, is_free=True)     # Libre
    ]

    # Dividimos el bloque 3 en dos hijos de 128KB
    root.children[1].children = [
        Block(id=4, size=128, is_free=True),   # Libre
        Block(id=5, size=128, is_free=True)    # Libre
    ]

    # Proceso de 100 KB
    process_size = 100
    required_size = get_required_block_size(process_size)
    print(f"Proceso: {process_size}KB → Se necesita bloque de {required_size}KB")

    best_block = find_best_fit_block(root, required_size)

    if best_block:
        print(f"Bloque asignado: {best_block}")
    else:
        print("No se encontró bloque disponible.")
