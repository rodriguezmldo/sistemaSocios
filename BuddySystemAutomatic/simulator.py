import random, json
from PyQt6.QtCore import QTimer

class Simulador:
    def __init__(self, sistema, actualizar_ui, n_procesos=200):
        self.sistema = sistema
        self.actualizar_ui = actualizar_ui
        self.procesos = self.generar_procesos(200)
        self.index = 0  # posición en la lista de procesos
        # Estados: "pendiente" (no intentado aún), "en ejecución", "finalizado", "no ejecutado"
        self.estados = {p["nombre"]: "pendiente" for p in self.procesos}

    def generar_procesos(self, n=200):
        procesos = []
        for i in range(n):
            nombre = f"P{i+1}"

            r = random.random() 
            if r < 0.7:  
                tamano = random.randint(1, 1024)
            else:  
                tamano = random.randint(1025, 2048)

            unidad = "KB"
            procesos.append({"nombre": nombre, "tamano": tamano, "unidad": unidad})

        # Guardar en archivo JSON
        with open("BuddySystemAutomatic/procesos.json", "w", encoding="utf-8") as f:
            json.dump(procesos, f, indent=2, ensure_ascii=False)

        return procesos
    
    def iniciar(self):
        self.procesar_lote()

    def procesar_lote(self):
        if self.index >= len(self.procesos):
            print("✅ Simulación finalizada")
            return

        lote = self.procesos[self.index:self.index+5]
        self.index += 5

        for p in lote:
            # Intentamos asignar cada proceso del lote
            self.asignar_proceso(p)

        # esperar 1 seg y luego seguir con el siguiente lote
        QTimer.singleShot(2500, self.procesar_lote)

    def asignar_proceso(self, p):
        nombre = p["nombre"]
        tam = convertir_a_bytes(p["tamano"], p["unidad"])
        nodo = self.sistema.asignar_memoria(tam, nombre)

        # Marcamos que ya fue intentado: si se asignó => "en ejecución", si no => "no ejecutado"
        if nodo:
            print(f"[+] Asignado {nombre} ({p['tamano']} {p['unidad']})")
            self.estados[nombre] = "en ejecución"
            self.actualizar_ui()
            # Liberar después de 2–3 seg
            t = random.randint(2000, 3000)
            QTimer.singleShot(t, lambda nombre=nombre, t=t: self.liberar_proceso(nombre, t))
        else:
            print(f"[!] No se pudo asignar {nombre} ({p['tamano']} {p['unidad']})")
            # Aumentamos el contador de "no ejecutados"
            self.estados[nombre] = "no ejecutado"
            self.actualizar_ui()

    def liberar_proceso(self, nombre, t):
        ok = self.sistema.liberar_memoria(nombre)
        if ok:
            print(f"[-] Liberado {nombre} después de {t/1000:.1f}s")
            # Solo marcar como finalizado si estaba en ejecución (seguro)
            self.estados[nombre] = "finalizado"
            self.actualizar_ui()

def convertir_a_bytes(valor: int, unidad: str) -> int:
    if unidad == "KB":
        return valor * 1024
    elif unidad == "MB":
        return valor * 1024 * 1024
    elif unidad == "GB":
        return valor * 1024 * 1024 * 1024
    else:  # Bytes
        return valor