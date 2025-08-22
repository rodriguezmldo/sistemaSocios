import tkinter as tk
from tkinter import ttk
import random


class TreeNode:
    def __init__(self, tamanio, father=None):
        self.tamanio = tamanio
        self.disponible = tamanio
        self.left = None
        self.right = None
        self.father = father
        self.ocupado = False
        self.proceso = ""
        self.visto = True
        self.representacion = None
        self.etiqueta = None
        self.coordenada = 0


class Tree:
    def __init__(self, tamanio):
        self.root = TreeNode(tamanio)
        self.asignados = 0
        self.memoria = 0

    def asignarMemoria(self, nodo, tamanio, proceso):
        """Simula asignación de memoria (simple)"""
        if nodo is None or nodo.ocupado:
            return None

        if tamanio <= nodo.disponible:
            nodo.ocupado = True
            nodo.proceso = proceso
            nodo.disponible -= tamanio
            return nodo
        else:
            # dividir si es necesario
            if nodo.left is None and nodo.right is None and nodo.tamanio > tamanio:
                mitad = nodo.tamanio // 2
                nodo.left = TreeNode(mitad, nodo)
                nodo.right = TreeNode(mitad, nodo)
                return self.asignarMemoria(nodo.left, tamanio, proceso)
            else:
                return self.asignarMemoria(nodo.left, tamanio, proceso) or self.asignarMemoria(nodo.right, tamanio, proceso)

    def liberarMemoria(self, nodo, proceso):
        if nodo is None:
            return
        if nodo.proceso == proceso:
            nodo.ocupado = False
            nodo.proceso = ""
            nodo.disponible = nodo.tamanio
        self.liberarMemoria(nodo.left, proceso)
        self.liberarMemoria(nodo.right, proceso)

    def memoriaDesperdiciada(self, nodo):
        if nodo is None:
            return 0
        desperdicio = 0
        if nodo.ocupado and nodo.disponible > 0:
            desperdicio += nodo.disponible
        desperdicio += self.memoriaDesperdiciada(nodo.left)
        desperdicio += self.memoriaDesperdiciada(nodo.right)
        return desperdicio


class Interfaz(tk.Tk):
    def __init__(self, T):
        super().__init__()
        self.T = T
        self.title("Buddy System - Python")
        self.geometry("1000x600")

        self.abecedario = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.enMemoria = ["" for _ in range(27)]
        self.opcionesNoVacias = []

        # Widgets principales
        self.canvas = tk.Canvas(self, bg="white", width=800, height=200)
        self.canvas.pack(pady=20)

        tk.Label(self, text="Asignar Memoria").pack()

        frame_input = tk.Frame(self)
        frame_input.pack()

        tk.Label(frame_input, text="Proceso:").grid(row=0, column=0)
        self.comboProcesos = ttk.Combobox(frame_input, values=self.abecedario)
        self.comboProcesos.grid(row=0, column=1)

        tk.Label(frame_input, text="Tamaño:").grid(row=1, column=0)
        self.txtTamanio = tk.Entry(frame_input)
        self.txtTamanio.grid(row=1, column=1)

        self.btnAsignar = tk.Button(frame_input, text="Asignar", command=self.btnAsignar_click)
        self.btnAsignar.grid(row=2, column=0, columnspan=2, pady=5)

        tk.Label(self, text="Liberar Memoria").pack()
        frame_lib = tk.Frame(self)
        frame_lib.pack()

        self.comboAsignados = ttk.Combobox(frame_lib, values=[])
        self.comboAsignados.grid(row=0, column=0)

        self.btnLiberar = tk.Button(frame_lib, text="Liberar", command=self.btnLiberar_click)
        self.btnLiberar.grid(row=0, column=1)

        frame_info = tk.Frame(self)
        frame_info.pack(pady=10)

        tk.Label(frame_info, text="Memoria Disponible:").grid(row=0, column=0)
        self.txtD = tk.Entry(frame_info)
        self.txtD.grid(row=0, column=1)

        tk.Label(frame_info, text="Memoria Desperdiciada:").grid(row=1, column=0)
        self.txtDesperdiciada = tk.Entry(frame_info)
        self.txtDesperdiciada.grid(row=1, column=1)

        self.update_info()

    def btnAsignar_click(self):
        proceso = self.comboProcesos.get()
        try:
            tamanio = int(self.txtTamanio.get())
        except:
            return

        nodo = self.T.asignarMemoria(self.T.root, tamanio, proceso)
        if nodo:
            self.enMemoria[self.T.asignados] = proceso
            self.T.asignados += 1
            if proceso in self.abecedario:
                self.abecedario.remove(proceso)
                self.comboProcesos["values"] = self.abecedario

            self.opcionesNoVacias = [p for p in self.enMemoria if p]
            self.comboAsignados["values"] = self.opcionesNoVacias

            self.dibujar_memoria(self.T.root)
            self.update_info()

    def btnLiberar_click(self):
        proceso = self.comboAsignados.get()
        if not proceso:
            return
        self.T.liberarMemoria(self.T.root, proceso)
        if proceso not in self.abecedario:
            self.abecedario.append(proceso)
            self.comboProcesos["values"] = self.abecedario

        self.enMemoria = [p for p in self.enMemoria if p != proceso] + [""]
        self.T.asignados -= 1
        self.opcionesNoVacias = [p for p in self.enMemoria if p]
        self.comboAsignados["values"] = self.opcionesNoVacias

        self.dibujar_memoria(self.T.root)
        self.update_info()

    def dibujar_memoria(self, nodo, x=50, y=50):
        if nodo is None:
            return
        width = nodo.tamanio * 4  # escala
        color = "#%06x" % random.randint(0x444444, 0xFFFFFF)
        self.canvas.create_rectangle(x, y, x + width, y + 40, fill=color, outline="black")
        label = nodo.proceso if nodo.ocupado else str(nodo.tamanio)
        self.canvas.create_text(x + width // 2, y + 20, text=label)

        if nodo.left:
            self.dibujar_memoria(nodo.left, x, y + 60)
        if nodo.right:
            self.dibujar_memoria(nodo.right, x + width // 2, y + 60)

    def update_info(self):
        self.txtD.delete(0, tk.END)
        self.txtD.insert(0, str(self.T.root.disponible))
        self.txtDesperdiciada.delete(0, tk.END)
        self.txtDesperdiciada.insert(0, str(self.T.memoriaDesperdiciada(self.T.root)))


if __name__ == "__main__":
    T = Tree(64)  # tamaño total de la memoria
    app = Interfaz(T)
    app.mainloop()
