# -*- coding: utf-8 -*-
"""
GUI del Buddy System con PyQt6

Características:
- Permite especificar "Tamaño de memoria (máxima)" y "Tamaño mínimo de bloque" para inicializar el sistema.
- Alta de procesos: nombre y tamaño solicitado.
- Eliminación de procesos desde una lista desplegable (ComboBox).
- Visualización de la memoria como barras horizontales proporcionadas al tamaño de los bloques.
- Muestra la fragmentación interna total (memoria desperdiciada).

Requisitos: PyQt6
    pip install PyQt6

Ejecutar:
    python BuddySystem_GUI_PyQt6.py
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QFont, QPen, QBrush
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QGroupBox, QLabel,
    QMessageBox, QComboBox, QFrame
)

# =========================
#   LÓGICA DEL BUDDY SYSTEM
# =========================

class NodoMemoria:
    def __init__(self, tamano: int):
        # Cada nodo representa un bloque de memoria
        self.proceso: Optional[str] = None      # Nombre del proceso que ocupa este bloque
        self.ocupado: bool = False              # Indica si el bloque está en uso
        self.tamano: int = tamano               # Tamaño del bloque (potencia de 2)
        self.tamOcupado: int = 0                # Tamaño real solicitado (para calcular desperdicio)
        self.padre: Optional[NodoMemoria] = None
        self.hijoIzquierdo: Optional[NodoMemoria] = None
        self.hijoDerecho: Optional[NodoMemoria] = None

    def es_hoja(self) -> bool:
        return self.hijoIzquierdo is None and self.hijoDerecho is None

    def __repr__(self):
        return f"<NodoMemoria tamano={self.tamano}, ocupado={self.ocupado}, proceso={self.proceso}>"


class SistemaBuddy:
    def __init__(self, tamano_total: int = 1024, tam_min_bloque: int = 1):
        # Ajustes a potencias de 2
        self.total = self.obtener_potencia_requerida(max(1, tamano_total))
        self.min_bloque = self.obtener_potencia_requerida(max(1, tam_min_bloque))
        if self.min_bloque > self.total:
            # Corrige caso extremo
            self.min_bloque = self.total
        # Árbol raíz
        self.raiz = NodoMemoria(self.total)

    @staticmethod
    def es_potencia_de_2(x: int) -> bool:
        return x > 0 and (x & (x - 1)) == 0

    @staticmethod
    def obtener_potencia_requerida(tamano: int) -> int:
        """Potencia de 2 más pequeña que sea >= tamaño"""
        potencia = 1
        while potencia < tamano:
            potencia <<= 1
        return potencia

    def _dividir(self, nodo: NodoMemoria):
        mitad = nodo.tamano // 2
        nodo.hijoIzquierdo = NodoMemoria(mitad)
        nodo.hijoDerecho = NodoMemoria(mitad)
        nodo.hijoIzquierdo.padre = nodo
        nodo.hijoDerecho.padre = nodo

    def asignar_memoria(self, espacio: int, proceso: str) -> Optional[NodoMemoria]:
        """Solicita memoria para un proceso aplicando buddy system"""
        if not proceso:
            return None
        espacio2 = self.obtener_potencia_requerida(espacio)
        if espacio2 > self.total:
            return None
        nodo = self._asignar(self.raiz, espacio2)
        if nodo:
            nodo.ocupado = True
            nodo.proceso = proceso
            nodo.tamOcupado = espacio
            return nodo
        return None

    def _asignar(self, nodo: NodoMemoria, espacio2: int) -> Optional[NodoMemoria]:
        # Si ocupado, no se puede usar
        if nodo.ocupado:
            return None

        # Si tiene hijos, intentar abajo
        if not nodo.es_hoja():
            return self._asignar(nodo.hijoIzquierdo, espacio2) or self._asignar(nodo.hijoDerecho, espacio2)

        # Es hoja libre
        if nodo.tamano < espacio2:
            return None

        if nodo.tamano == espacio2:
            return nodo

        # nodo.tamano > espacio2, decidir si dividir o asignar completo si no podemos dividir
        # Podemos dividir si la mitad es >= al máximo entre el espacio requerido y el tamaño mínimo de bloque
        mitad = nodo.tamano // 2
        if mitad >= max(espacio2, self.min_bloque):
            self._dividir(nodo)
            return self._asignar(nodo.hijoIzquierdo, espacio2) or self._asignar(nodo.hijoDerecho, espacio2)
        else:
            # No podemos dividir más por restricción de mínimo; asignar este bloque completo
            return nodo

    def liberar_memoria(self, proceso: str) -> bool:
        nodo = self._buscar_nodo(self.raiz, proceso)
        if not nodo:
            return False
        nodo.ocupado = False
        nodo.proceso = None
        nodo.tamOcupado = 0
        self._fusionar(nodo)
        return True

    def _buscar_nodo(self, nodo: Optional[NodoMemoria], proceso: str) -> Optional[NodoMemoria]:
        if nodo is None:
            return None
        if nodo.proceso == proceso:
            return nodo
        return self._buscar_nodo(nodo.hijoIzquierdo, proceso) or self._buscar_nodo(nodo.hijoDerecho, proceso)

    def _fusionar(self, nodo: NodoMemoria):
        padre = nodo.padre
        if padre and padre.hijoIzquierdo and padre.hijoDerecho:
            izq = padre.hijoIzquierdo
            der = padre.hijoDerecho
            # Fusionar sólo si ambos son hojas y libres
            if (not izq.ocupado and not der.ocupado and izq.es_hoja() and der.es_hoja()):
                padre.hijoIzquierdo = None
                padre.hijoDerecho = None
                padre.ocupado = False
                self._fusionar(padre)

    def memoria_desperdiciada(self, nodo: Optional[NodoMemoria] = None) -> int:
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

    # Utilidades para GUI
    def hojas_en_orden(self) -> List[NodoMemoria]:
        """Retorna la lista de bloques hoja de izquierda a derecha"""
        hojas: List[NodoMemoria] = []

        def _inorden(n: Optional[NodoMemoria]):
            if n is None:
                return
            if n.es_hoja():
                hojas.append(n)
            else:
                _inorden(n.hijoIzquierdo)
                _inorden(n.hijoDerecho)
        _inorden(self.raiz)
        return hojas

    def procesos_vigentes(self) -> List[str]:
        vistos = set()
        nombres: List[str] = []

        def _rec(n: Optional[NodoMemoria]):
            if n is None:
                return
            if n.ocupado and n.proceso and n.proceso not in vistos:
                vistos.add(n.proceso)
                nombres.append(n.proceso)
            _rec(n.hijoIzquierdo)
            _rec(n.hijoDerecho)
        _rec(self.raiz)
        return sorted(nombres)


# =========================
#   WIDGET DE DIBUJO (BARRAS)
# =========================
class MemoriaView(QWidget):
    """Dibuja la memoria como una barra segmentada proporcional al tamaño de cada hoja"""
    def __init__(self, get_sistema_callable, parent=None):
        super().__init__(parent)
        self.get_sistema = get_sistema_callable
        self.setMinimumHeight(180)
        self.setAutoFillBackground(True)
        self.setToolTip("Visualización de bloques: Ocupado=relleno, Libre=rayado. Borde indica tamaño del bloque.")

    def paintEvent(self, event):
        sys: Optional[SistemaBuddy] = self.get_sistema()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect_total = self.rect().adjusted(10, 20, -10, -20)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawRect(rect_total)

        if not sys:
            painter.drawText(rect_total, Qt.AlignmentFlag.AlignCenter, "Inicializa el sistema para visualizar")
            painter.end()
            return

        hojas = sys.hojas_en_orden()
        if not hojas:
            painter.drawText(rect_total, Qt.AlignmentFlag.AlignCenter, "Sin bloques")
            painter.end()
            return

        x = rect_total.left()
        alto = rect_total.height()
        escala = rect_total.width() / float(sys.total)

        fuente = QFont()
        fuente.setPointSize(9)
        painter.setFont(fuente)

        for nodo in hojas:
            ancho = nodo.tamano * escala
            bloque = QRectF(x, rect_total.top(), ancho, alto)

            # Color/estilo según estado
            if nodo.ocupado:
                painter.setBrush(QBrush(Qt.GlobalColor.darkCyan))
            else:
                # Libre: hacer un rayado
                painter.setBrush(Qt.BrushStyle.Dense4Pattern)

            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            painter.drawRect(bloque)

            # Texto informativo dentro del bloque
            info = []
            if nodo.ocupado and nodo.proceso:
                info.append(f"{nodo.proceso}")
                info.append(f"{nodo.tamOcupado}/{nodo.tamano}")
            else:
                info.append("LIBRE")
                info.append(f"{nodo.tamano}")
            texto = "\n".join(info)
            painter.drawText(bloque, Qt.AlignmentFlag.AlignCenter, texto)

            x += ancho

        painter.end()


# =========================
#   APLICACIÓN / INTERFAZ
# =========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buddy System - Administrador de Memoria (PyQt6)")
        self.setMinimumSize(900, 560)

        self.sistema: Optional[SistemaBuddy] = None

        cont = QWidget()
        self.setCentralWidget(cont)
        layout = QVBoxLayout(cont)

        # --- Panel de inicialización ---
        init_group = QGroupBox("Inicialización del Sistema")
        f = QFormLayout()
        self.spin_total = QSpinBox()
        self.spin_total.setRange(1, 1_073_741_824)  # hasta 1 GB en unidades arbitrarias
        self.spin_total.setValue(1024)
        self.spin_total.setSingleStep(1)
        self.spin_total.setToolTip("Tamaño total de la memoria. Se ajustará a potencia de 2.")

        self.spin_min = QSpinBox()
        self.spin_min.setRange(1, 1_073_741_824)
        self.spin_min.setValue(32)
        self.spin_min.setToolTip("Tamaño mínimo de bloque al dividir. Se ajustará a potencia de 2.")

        btn_init = QPushButton("Inicializar")
        btn_init.clicked.connect(self.on_inicializar)

        f.addRow("Memoria total:", self.spin_total)
        f.addRow("Bloque mínimo:", self.spin_min)
        f.addRow(btn_init)
        init_group.setLayout(f)

        # --- Panel de operaciones ---
        ops_group = QGroupBox("Operaciones")
        ops_layout = QFormLayout()

        self.edit_nombre = QLineEdit()
        self.edit_nombre.setPlaceholderText("Nombre del proceso (p.ej. A, B, Juego, etc.)")
        self.edit_tamano = QSpinBox()
        self.edit_tamano.setRange(1, 1_073_741_824)
        self.edit_tamano.setValue(200)

        btn_add = QPushButton("Asignar proceso")
        btn_add.clicked.connect(self.on_asignar)

        self.combo_borrar = QComboBox()
        self.combo_borrar.setPlaceholderText("Selecciona proceso a liberar")
        btn_free = QPushButton("Liberar proceso")
        btn_free.clicked.connect(self.on_liberar)

        ops_layout.addRow("Nombre:", self.edit_nombre)
        ops_layout.addRow("Tamaño solicitado:", self.edit_tamano)
        ops_layout.addRow(btn_add)

        ops_layout.addRow(QLabel("\nEliminar proceso:"))
        ops_layout.addRow("Proceso:", self.combo_borrar)
        ops_layout.addRow(btn_free)
        ops_group.setLayout(ops_layout)

        # --- Indicadores ---
        info_bar = QHBoxLayout()
        self.lbl_estado = QLabel("Sin inicializar")
        self.lbl_estado.setStyleSheet("font-weight: bold;")
        self.lbl_frag = QLabel("Desperdicio: 0")
        info_bar.addWidget(self.lbl_estado, 1)
        info_bar.addWidget(self.lbl_frag, 0)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

        # --- Vista de memoria ---
        self.mem_view = MemoriaView(self.get_sistema)

        # Ensamblar layout principal
        top = QHBoxLayout()
        top.addWidget(init_group, 1)
        top.addWidget(ops_group, 1)

        layout.addLayout(top)
        layout.addLayout(info_bar)
        layout.addWidget(sep)
        layout.addWidget(self.mem_view, 1)

    # --------- Callbacks ---------
    def get_sistema(self) -> Optional[SistemaBuddy]:
        return self.sistema

    def on_inicializar(self):
        total = int(self.spin_total.value())
        minbloq = int(self.spin_min.value())

        # Ajuste a potencias de 2 y validaciones
        total_pow2 = SistemaBuddy.obtener_potencia_requerida(total)
        min_pow2 = SistemaBuddy.obtener_potencia_requerida(minbloq)

        if min_pow2 > total_pow2:
            QMessageBox.warning(self, "Valores inválidos", "El bloque mínimo no puede ser mayor que la memoria total.")
            return

        if not SistemaBuddy.es_potencia_de_2(total):
            QMessageBox.information(self, "Ajuste realizado",
                                    f"Memoria total {total} ajustada a potencia de 2: {total_pow2}")
        if not SistemaBuddy.es_potencia_de_2(minbloq):
            QMessageBox.information(self, "Ajuste realizado",
                                    f"Bloque mínimo {minbloq} ajustado a potencia de 2: {min_pow2}")

        self.sistema = SistemaBuddy(total_pow2, min_pow2)
        self.actualizar_ui()

    def on_asignar(self):
        if not self.sistema:
            QMessageBox.warning(self, "No inicializado", "Primero inicializa el sistema.")
            return
        nombre = self.edit_nombre.text().strip()
        tam = int(self.edit_tamano.value())
        if not nombre:
            QMessageBox.warning(self, "Dato faltante", "Ingresa un nombre para el proceso.")
            return

        nodo = self.sistema.asignar_memoria(tam, nombre)
        if nodo is None:
            QMessageBox.critical(self, "Sin espacio", "No se pudo asignar memoria al proceso (espacio insuficiente o fragmentación).")
        self.actualizar_ui()

    def on_liberar(self):
        if not self.sistema:
            QMessageBox.warning(self, "No inicializado", "Primero inicializa el sistema.")
            return
        proc = self.combo_borrar.currentText().strip()
        if not proc:
            QMessageBox.information(self, "Seleccione", "No hay proceso seleccionado.")
            return
        ok = self.sistema.liberar_memoria(proc)
        if not ok:
            QMessageBox.information(self, "No encontrado", "Ese proceso no existe o ya fue liberado.")
        self.actualizar_ui()

    def actualizar_ui(self):
        # Actualiza combo de procesos, etiqueta de desperdicio y redibuja
        if self.sistema:
            procesos = self.sistema.procesos_vigentes()
            self.combo_borrar.clear()
            self.combo_borrar.addItems(procesos)
            desperdicio = self.sistema.memoria_desperdiciada()
            self.lbl_frag.setText(f"Desperdicio: {desperdicio}")
            self.lbl_estado.setText(
                f"Total: {self.sistema.total} | Mín. bloque: {self.sistema.min_bloque}"
            )
        else:
            self.combo_borrar.clear()
            self.lbl_frag.setText("Desperdicio: 0")
            self.lbl_estado.setText("Sin inicializar")

        self.mem_view.update()


# =========================
#   MAIN
# =========================

def main():
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
