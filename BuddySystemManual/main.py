# -*- coding: utf-8 -*-
"""
GUI del Buddy System con PyQt6

Características:
- Permite especificar "Tamaño de memoria (máxima)" y "Tamaño mínimo de bloque" para inicializar el sistema.
- Alta de procesos: nombre y tamaño solicitado.
- Eliminación de procesos desde una lista desplegable 
- Visualización de la memoria como barras horizontales proporcionadas al tamaño de los bloques.
- Muestra la fragmentación interna total (memoria desperdiciada).
- Bloques buddies (socios) tienen el mismo color.

Requisitos: PyQt6
    pip install PyQt6

Ejecutar:
    python BuddySystem_GUI_PyQt6.py

Miembros: 
- José Antonio Rodriguez Maldonado
- José Luis Santiago Ibañez 
- Jorge Luis Vergara Mora
- Alan Salomon Sanabia Santos
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple
import hashlib

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QFont, QPen, QBrush, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QGroupBox, QLabel,
    QMessageBox, QComboBox, QFrame
)

from PyQt6.QtGui import QValidator
import math
from BuddySystem import SistemaBuddy, NodoMemoria



class PowerOfTwoSpinBox(QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRange(1, 1_073_741_824)
        self.setValue(1024)

    def stepBy(self, steps: int) -> None:
        val = self.value()
        exp = int(round(math.log2(val)))
        new_exp = exp + steps
        new_exp = max(0, min(new_exp, 30))
        self.setValue(2 ** new_exp)

    def validate(self, text: str, pos: int):
        try:
            v = int(text)
            if v > 0 and (v & (v - 1)) == 0:
                return (QValidator.State.Acceptable, text, pos)
            return (QValidator.State.Intermediate, text, pos)
        except:
            return (QValidator.State.Invalid, text, pos)


# =========================
#           UNIDADES
# =========================

def convertir_a_bytes(valor: int, unidad: str) -> int:
    if unidad == "KB":
        return valor * 1024
    elif unidad == "MB":
        return valor * 1024 * 1024
    elif unidad == "GB":
        return valor * 1024 * 1024 * 1024
    else: 
        return valor

def formatear_tamano(bytes_val: int) -> str:
    if bytes_val >= 1024*1024*1024:
        return f"{bytes_val // (1024*1024*1024)} GB"
    elif bytes_val >= 1024*1024:
        return f"{bytes_val // (1024*1024)} MB"
    elif bytes_val >= 1024:
        return f"{bytes_val // 1024} KB"
    else:
        return f"{bytes_val} B"


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
        self.colores_buddies = {}  # Cache de colores para buddies

    def obtener_color_para_bloque(self, nodo: NodoMemoria) -> QColor:
        """Genera un color único para cada par de bloques buddies"""
        # Para bloques libres, usar un color especial
        if not nodo.ocupado:
            return QColor(200, 200, 200)  # Gris para bloques libres
        
        # Calcular la dirección base del par de buddies
        # Los buddies comparten la misma dirección base (la del bloque padre)
        buddy_address = self.get_sistema().obtener_buddy_address(nodo.direccion, nodo.tamano)
        base_address = min(nodo.direccion, buddy_address)
        
        # Generar un color único basado en la dirección base
        if base_address not in self.colores_buddies:
            # Usar hash para generar un color consistente
            hash_obj = hashlib.md5(str(base_address).encode())
            hash_val = int(hash_obj.hexdigest()[:8], 16)
            
            # Generar color a partir del hash (evitando colores muy claros)
            r = (hash_val & 0xFF) % 200  # Limitar a máximo 200 para evitar colores muy claros
            g = ((hash_val >> 8) & 0xFF) % 200
            b = ((hash_val >> 16) & 0xFF) % 200
            
            self.colores_buddies[base_address] = QColor(r, g, b)
        
        return self.colores_buddies[base_address]

    def paintEvent(self, event):
        sys: Optional[SistemaBuddy] = self.get_sistema()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect_total = self.rect().adjusted(10, 20, -10, -20)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
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
                color = self.obtener_color_para_bloque(nodo)
                painter.setBrush(QBrush(color))
            else:
                # Libre: hacer un rayado
                painter.setBrush(Qt.BrushStyle.Dense4Pattern)

            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            painter.drawRect(bloque)

            # Texto informativo dentro del bloque
            info = []
            if nodo.ocupado and nodo.proceso:
                info.append(f"{nodo.proceso}")
                info.append(f"{formatear_tamano(nodo.tamOcupado)}/{formatear_tamano(nodo.tamano)}")
            else:
                info.append("LIBRE")
                info.append(f"{formatear_tamano(nodo.tamano)}")

            texto = "\n".join(info)
            painter.drawText(bloque, Qt.AlignmentFlag.AlignCenter, texto)

            x += ancho

        painter.end()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buddy System - Administrador de Memoria (PyQt6)")
        self.setMinimumSize(900, 560)

        self.sistema: Optional[SistemaBuddy] = None

        cont = QWidget()
        self.setCentralWidget(cont)
        layout = QVBoxLayout(cont)

        init_group = QGroupBox("Inicialización del Sistema")
        f = QFormLayout()

        # SpinBox + Unidad
        self.spin_total = PowerOfTwoSpinBox()
        self.spin_total.setValue(1024)
        self.combo_total_unit = QComboBox()
        self.combo_total_unit.addItems(["B", "KB", "MB", "GB"])
        self.combo_total_unit.setCurrentText("KB")

        self.spin_min = PowerOfTwoSpinBox()
        self.spin_min.setValue(32)
        self.combo_min_unit = QComboBox()
        self.combo_min_unit.addItems(["B", "KB", "MB", "GB"])
        self.combo_min_unit.setCurrentText("B")

        btn_init = QPushButton("Inicializar")
        btn_init.clicked.connect(self.on_inicializar)

        row_total = QHBoxLayout()
        row_total.addWidget(self.spin_total)
        row_total.addWidget(self.combo_total_unit)

        row_min = QHBoxLayout()
        row_min.addWidget(self.spin_min)
        row_min.addWidget(self.combo_min_unit)

        f.addRow("Memoria total:", row_total)
        f.addRow("Bloque mínimo:", row_min)
        f.addRow(btn_init)
        init_group.setLayout(f)

        # --- Panel de operaciones ---
        ops_group = QGroupBox("Operaciones")
        ops_layout = QFormLayout()

        self.edit_nombre = QLineEdit()
        self.edit_nombre.setPlaceholderText("Nombre del proceso (p.ej. A, B, Juego, etc.)")

        # SpinBox + Unidad
        self.edit_tamano = QSpinBox()
        self.edit_tamano.setRange(1, 1_073_741_824)
        self.edit_tamano.setValue(200)
        self.combo_proc_unit = QComboBox()
        self.combo_proc_unit.addItems(["B", "KB", "MB", "GB"])
        self.combo_proc_unit.setCurrentText("B")

        row_proc = QHBoxLayout()
        row_proc.addWidget(self.edit_tamano)
        row_proc.addWidget(self.combo_proc_unit)

        btn_add = QPushButton("Asignar proceso")
        btn_add.clicked.connect(self.on_asignar)

        self.combo_borrar = QComboBox()
        self.combo_borrar.setPlaceholderText("Selecciona proceso a liberar")
        btn_free = QPushButton("Liberar proceso")
        btn_free.clicked.connect(self.on_liberar)

        ops_layout.addRow("Nombre:", self.edit_nombre)
        ops_layout.addRow("Tamaño solicitado:", row_proc)
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
        # Convertir a bytes
        total = convertir_a_bytes(self.spin_total.value(), self.combo_total_unit.currentText())
        minbloq = convertir_a_bytes(self.spin_min.value(), self.combo_min_unit.currentText())

        # Ajuste a potencias de 2 y validaciones
        total_pow2 = SistemaBuddy.obtener_potencia_requerida(total)
        min_pow2 = SistemaBuddy.obtener_potencia_requerida(minbloq)

        if min_pow2 > total_pow2:
            QMessageBox.warning(self, "Valores inválidos", "El bloque mínimo no puede ser mayor que la memoria total.")
            return

        self.sistema = SistemaBuddy(total_pow2, min_pow2)
        self.actualizar_ui()

    def on_asignar(self):
        if not self.sistema:
            QMessageBox.warning(self, "No inicializado", "Primero inicializa el sistema.")
            return

        nombre = self.edit_nombre.text().strip()
        tam = convertir_a_bytes(self.edit_tamano.value(), self.combo_proc_unit.currentText())

        if not nombre:
            QMessageBox.warning(self, "Dato faltante", "Ingresa un nombre para el proceso.")
            return

        if nombre in self.sistema.procesos_vigentes():
            QMessageBox.warning(self, "Duplicado", f"Ya existe un proceso con el nombre '{nombre}'.")
            return

        nodo = self.sistema.asignar_memoria(tam, nombre)
        if nodo is None:
            QMessageBox.critical(
                self, "Sin espacio",
                "No se pudo asignar memoria al proceso (espacio insuficiente o fragmentación)."
            )

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
        if self.sistema:
            procesos = self.sistema.procesos_vigentes()
            self.combo_borrar.clear()
            self.combo_borrar.addItems(procesos)
            desperdicio = formatear_tamano(self.sistema.memoria_desperdiciada())
            self.lbl_frag.setText(f"Desperdicio: {desperdicio}")
            self.lbl_estado.setText(
                f"Total: {formatear_tamano(self.sistema.total)} | Mín. bloque: {formatear_tamano(self.sistema.min_bloque)}"
            )
        else:
            self.combo_borrar.clear()
            self.lbl_frag.setText("Desperdicio: 0")
            self.lbl_estado.setText("Sin inicializar")

        self.mem_view.update()


# -------- Funciones auxiliares --------
def convertir_a_bytes(valor: int, unidad: str) -> int:
    factor = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
    return valor * factor[unidad]


def formatear_tamano(bytes_val: int) -> str:
    for unidad in ["B", "KB", "MB", "GB"]:
        if bytes_val < 1024 or unidad == "GB":
            return f"{bytes_val:.0f} {unidad}"
        bytes_val /= 1024


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