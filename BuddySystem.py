class NodoMemoria:
    def __init__(self, tamano):
        # Cada nodo representa un bloque de memoria
        self.proceso = None            # Nombre del proceso que ocupa este bloque
        self.ocupado = False           # Indica si el bloque está en uso
        self.tamano = tamano           # Tamaño del bloque (siempre potencia de 2)
        self.tamOcupado = 0            # Tamaño real solicitado (para calcular desperdicio)
        self.padre = None              # Referencia al bloque padre
        self.hijoIzquierdo = None      # Bloque hijo izquierdo
        self.hijoDerecho = None        # Bloque hijo derecho 

    def __repr__(self):
        return f"<NodoMemoria tamano={self.tamano}, ocupado={self.ocupado}, proceso={self.proceso}>"


class SistemaBuddy:
    def __init__(self, tamano=1024):
        # Ajusta el tamaño inicial a la potencia de 2 más cercana
        self.total = self.obtener_potencia_requerida(tamano)
        # El árbol arranca con un único bloque raíz
        self.raiz = NodoMemoria(self.total)

    @staticmethod
    def obtener_potencia_requerida(tamano):
        """Encuentra la potencia de 2 más pequeña que sea >= tamaño"""
        potencia = 1
        while potencia < tamano:
            potencia *= 2
        return potencia

    def _dividir(self, nodo: NodoMemoria):
        """Parte un bloque en dos mitades (buddies)"""
        mitad = nodo.tamano // 2
        nodo.hijoIzquierdo = NodoMemoria(mitad)
        nodo.hijoDerecho = NodoMemoria(mitad)
        nodo.hijoIzquierdo.padre = nodo
        nodo.hijoDerecho.padre = nodo

    def asignar_memoria(self, espacio: int, proceso: str):
        """Solicita memoria para un proceso aplicando buddy system"""
        print(f"\n➡️ Proceso {proceso} solicita {espacio} unidades")
        
        # Se ajusta el tamaño pedido a la potencia de 2
        espacio2 = self.obtener_potencia_requerida(espacio)

        # Si el proceso pide más que la memoria total, se rechaza
        if espacio2 > self.total:
            print("❌ No hay suficiente memoria total")
            return None

        # Se busca un bloque disponible
        nodo = self._asignar(self.raiz, espacio2)
        #print("\nMemoria Desperdiciada: ",self.memoria_desperdiciada())

        if nodo:
            nodo.ocupado = True
            nodo.proceso = proceso
            nodo.tamOcupado = espacio
            print(f"✅ Proceso {proceso} asignado en bloque de {nodo.tamano}\n")
        else:
            print("❌ No se encontró bloque disponible")

        


    def _asignar(self, nodo: NodoMemoria, espacio2: int):
        """Recorre el árbol para encontrar un bloque libre del tamaño justo"""
        if nodo.ocupado:
            return None
        if nodo.tamano == espacio2 and not nodo.hijoIzquierdo:
            return nodo
        if nodo.tamano > espacio2:
            # Si aún no está dividido, se parte en dos
            if not nodo.hijoIzquierdo:
                self._dividir(nodo)
            # Se intenta asignar primero a la izquierda, si no, a la derecha
            return self._asignar(nodo.hijoIzquierdo, espacio2) or self._asignar(nodo.hijoDerecho, espacio2)
        return None

    def liberar_memoria(self, proceso: str):
        """Libera la memoria asignada a un proceso y fusiona bloques si es posible"""
        nodo = self._buscar_nodo(self.raiz, proceso)
        if not nodo:
            print(f"⚠️ Proceso {proceso} no encontrado")
            return

        print(f"\n♻️ Liberando proceso {proceso} del bloque de {nodo.tamano}\n")
        nodo.ocupado = False
        nodo.proceso = None
        nodo.tamOcupado = 0
        self._fusionar(nodo)

        #print("\nMemoria Desperdiciada: ",self.memoria_desperdiciada())


    def _buscar_nodo(self, nodo: NodoMemoria, proceso: str):
        """Busca en el árbol el bloque donde está un proceso"""
        if not nodo:
            return None
        if nodo.proceso == proceso:
            return nodo
        return self._buscar_nodo(nodo.hijoIzquierdo, proceso) or self._buscar_nodo(nodo.hijoDerecho, proceso)

    def _fusionar(self, nodo: NodoMemoria):
        """Intenta fusionar dos bloques hermanos si ambos están libres"""
        padre = nodo.padre
        if padre and padre.hijoIzquierdo and padre.hijoDerecho:
            # Solo se fusionan si ambos hijos están libres y no han sido subdivididos
            if (not padre.hijoIzquierdo.ocupado and not padre.hijoDerecho.ocupado 
                and not padre.hijoIzquierdo.hijoIzquierdo and not padre.hijoDerecho.hijoDerecho):
                padre.hijoIzquierdo = None
                padre.hijoDerecho = None
                padre.ocupado = False
                # Se intenta seguir fusionando hacia arriba
                self._fusionar(padre)

    def memoria_desperdiciada(self, nodo: NodoMemoria = None):
        """Suma el desperdicio de memoria (fragmentación interna)"""
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

    def mostrar(self, nodo: NodoMemoria = None, nivel=0, raiz=True):
        """Imprime la estructura jerárquica de la memoria y al final la fragmentación"""
        if nodo is None:
            nodo = self.raiz
        if nodo:
            # Si el bloque está subdividido, no se muestra guion ni proceso
            if nodo.hijoIzquierdo or nodo.hijoDerecho:
                print("  " * nivel + f"[{nodo.tamano}] Subdividido")
            else:
                estado = "Ocupado" if nodo.ocupado else "Libre"
                print("  " * nivel + f"[{nodo.tamano}] {estado} - {nodo.proceso}")
    
            # Recorrer hijos
            if nodo.hijoIzquierdo:
                self.mostrar(nodo.hijoIzquierdo, nivel + 1, raiz=False)
            if nodo.hijoDerecho:
                self.mostrar(nodo.hijoDerecho, nivel + 1, raiz=False)
    
        # Solo imprimir la memoria desperdiciada una vez (al terminar el árbol completo)
        if raiz:
            desperdicio = self.memoria_desperdiciada()
            print(f"\n💾 Memoria desperdiciada (fragmentación interna): {desperdicio}\n")


# Ejemplo de uso
if __name__ == "__main__":
    on = True

    print("  ==== BUDDY SYSTEM ADMINISTRADOR DE MEMORIA ==== ")

    # Validar tamaño de memoria como potencia de 2
    while True:
        print("Tamaño de memoria: ")
        entrada = int(input())  # convertir a entero
        if entrada > 0 and (entrada & (entrada - 1)) == 0:
            memoria = SistemaBuddy(entrada)
            print(f"Memoria válida: {entrada}")
            break  # salir del bucle al ingresar un tamaño válido
        else:
            print("❌ El tamaño debe ser potencia de 2. Intente de nuevo.")

    # Menú principal
    on = True
    while on: 
        print("\nOpciones")
        print("1.- Asignar memoria ")
        print("2.- Liberar memoria ")
        print("3.- Salir")

        print("Entrada: ")
        entrada = int(input())

        if entrada == 1: 
            print("Letra para el Proceso: ")
            letraProceso = input().strip().upper()  # limpio y mayúscula
            print("Tamaño del Proceso: ")
            entradaProceso = int(input())

            if entradaProceso > 0: 
                memoria.asignar_memoria(entradaProceso, letraProceso)
                memoria.mostrar()
            else: 
                print("⚠ Tamaño del proceso invalido")

        elif entrada == 2: 
            print("Letra para el Proceso: ")
            letraProceso = input().strip().upper()
            memoria.liberar_memoria(letraProceso)
            memoria.mostrar()

        elif entrada == 3:
            print("👋 Saliendo del administrador de memoria...")
            on = False

        else:
            print("⚠ Opción no disponible -- intente de nuevo")



"""     memoria.asignar_memoria(200, "A") 
    memoria.mostrar()
    print("\nMemoria Desperdiciada: ",memoria.memoria_desperdiciada())

    memoria.asignar_memoria(200, "B")
    memoria.mostrar()
    print("\nMemoria Desperdiciada: ",memoria.memoria_desperdiciada())

    memoria.asignar_memoria(200, "C")
    memoria.mostrar()
    print("\nMemoria Desperdiciada: ",memoria.memoria_desperdiciada())

    memoria.asignar_memoria(200, "D")
    memoria.mostrar()
    print("\nMemoria Desperdiciada: ",memoria.memoria_desperdiciada())

    memoria.liberar_memoria("A")
    memoria.mostrar()
    print("\nMemoria Desperdiciada: ",memoria.memoria_desperdiciada())

    memoria.liberar_memoria("B")
    memoria.mostrar()
    print("\nMemoria Desperdiciada: ",memoria.memoria_desperdiciada())
    #print("\nMemoria desperdiciada:", memoria.memoria_desperdiciada()) """
