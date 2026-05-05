"""
Práctica III – POO
Generador de Árbol de Derivación y AST para Gramáticas Libres de Contexto (GLC)

Lenguaje : Python 3.10+
Interfaz : Tkinter
Librerías: nltk, matplotlib, networkx

Instalación:
    pip install nltk matplotlib networkx

Ejecución:
    python practica_glc.py

Formato de la gramática (BNF de NLTK):
    S -> E
    E -> E '+' T | E '-' T | T
    ...
    Los terminales van entre comillas simples.

Formato de la expresión:
    Tokens separados por espacios. Los números y variables se normalizan
    automáticamente a 'num' e 'id' respectivamente.
    Ejemplo: 4 + x * 3   →   num + id * num
"""

import re
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
import networkx as nx
from nltk import CFG, Tree
from nltk.parse.earleychart import EarleyChartParser

# ─────────────────────────────────────────────────────────────────────────── #
# Gramática y expresión por defecto                                           #
# ─────────────────────────────────────────────────────────────────────────── #

GRAMATICA_DEFAULT = """\
S -> E
E -> E '+' T | E '-' T | T
T -> T '*' F | T '/' F | F
F -> '(' E ')' | 'num' | 'id'"""

EXPRESION_DEFAULT = "4 + x * 3"


# ─────────────────────────────────────────────────────────────────────────── #
# Modelo: carga la gramática y analiza la expresión                           #
# ─────────────────────────────────────────────────────────────────────────── #

class ModeloGramatica:
    """Carga la GLC y convierte la expresión del usuario en tokens válidos."""

    def __init__(self, texto: str):
        self.gramatica = CFG.fromstring(texto)
        self.parser = EarleyChartParser(self.gramatica, trace=0)

    def tokenizar(self, expresion: str) -> list[str]:
        """
        Normaliza cada token de la expresión:
          - Número  (4, 3.14)       → 'num'
          - Variable (x, edad)      → 'id'
          - Operador (+, -, *, /)   → sin cambio
          - Paréntesis              → sin cambio
        """
        tokens = []
        for tok in expresion.strip().split():
            if re.fullmatch(r"\d+(\.\d+)?", tok):
                tokens.append("num")
            elif re.fullmatch(r"[a-zA-Z_]\w*", tok):
                tokens.append("id")
            elif tok in ("+", "-", "*", "/", "(", ")"):
                tokens.append(tok)
            else:
                raise ValueError(
                    f"Token no reconocido: '{tok}'\n"
                    "Separa todos los elementos con espacios. Ej: 4 + x * 3"
                )
        return tokens

    def parsear(self, expresion: str) -> tuple:
        """Retorna (árbol, tokens). El árbol es None si la expresión es inválida."""
        tokens = self.tokenizar(expresion)
        arboles = list(self.parser.parse(tokens))
        return (arboles[0] if arboles else None), tokens


# ─────────────────────────────────────────────────────────────────────────── #
# Generador de derivación izquierda / derecha                                 #
# ─────────────────────────────────────────────────────────────────────────── #

class GeneradorDerivacion:
    """
    Genera los pasos de derivación a partir de un árbol de derivación.

    Derivación izquierda: se expande siempre el no-terminal más a la izquierda.
    Derivación derecha:   se expande siempre el no-terminal más a la derecha.
    """

    def __init__(self, arbol: Tree):
        self._arbol = arbol

    def derivar(self, izquierda: bool = True) -> list[str]:
        pasos = [self._arbol.label()]   # forma sentencial inicial
        actual = [self._arbol.label()]
        self._derivar_nodo(self._arbol, actual, pasos, izquierda)
        return pasos

    def _derivar_nodo(self, nodo, actual: list, pasos: list, izquierda: bool):
        if isinstance(nodo, str):
            return

        # Reemplazo: etiquetas de los hijos directos
        simbolo = nodo.label()
        reemplazo = [h.label() if isinstance(h, Tree) else h for h in nodo]

        # Buscar la ocurrencia correcta (izquierda ↔ la primera; derecha ↔ la última)
        idx = self._buscar(actual, simbolo, izquierda)
        if idx != -1:
            actual[idx : idx + 1] = reemplazo
            pasos.append(" ".join(actual))

        # Recorrer hijos en el orden adecuado
        hijos = list(nodo) if izquierda else list(reversed(nodo))
        for hijo in hijos:
            if isinstance(hijo, Tree):
                self._derivar_nodo(hijo, actual, pasos, izquierda)

    @staticmethod
    def _buscar(lista: list, simbolo: str, izquierda: bool) -> int:
        rango = range(len(lista)) if izquierda else range(len(lista) - 1, -1, -1)
        for i in rango:
            if lista[i] == simbolo:
                return i
        return -1


# ─────────────────────────────────────────────────────────────────────────── #
# Constructor del AST                                                         #
# ─────────────────────────────────────────────────────────────────────────── #

class GeneradorAST:
    """
    Simplifica el árbol de derivación para producir el AST.

    Reglas de simplificación:
      1. Elimina paréntesis (nodos terminales '(' y ')').
      2. Colapsa nodos con un único hijo (reglas unitarias / cadenas).
      3. Para expresiones binarias (izq, operador, der), convierte el
         operador en raíz: op(izq, der).
    """

    OPERADORES = {"+", "-", "*", "/"}
    OMITIR     = {"(", ")"}

    def generar(self, arbol: Tree) -> Tree:
        resultado = self._simplificar(arbol)
        # Si todo colapsa a un terminal, lo envolvemos
        if not isinstance(resultado, Tree):
            return Tree(str(resultado), [])
        return resultado

    def _simplificar(self, nodo):
        # Terminal
        if isinstance(nodo, str):
            return None if nodo in self.OMITIR else Tree(nodo, [])

        # Simplificar hijos
        hijos = []
        for h in nodo:
            s = self._simplificar(h)
            if s is not None:
                hijos.append(s)

        # Regla unitaria: colapsar hacia el hijo
        if len(hijos) == 1:
            return hijos[0]

        # Expresión binaria: (izq, operador, der) → op(izq, der)
        if len(hijos) == 3 and hijos[1].label() in self.OPERADORES:
            return Tree(hijos[1].label(), [hijos[0], hijos[2]])

        return Tree(nodo.label(), hijos)


# ─────────────────────────────────────────────────────────────────────────── #
# Visualizador de árboles (NetworkX + Matplotlib)                             #
# ─────────────────────────────────────────────────────────────────────────── #

class VisualizadorArbol:
    """Dibuja un árbol NLTK en una ventana Matplotlib usando NetworkX."""

    def mostrar(self, arbol: Tree, titulo: str):
        grafo   = nx.DiGraph()
        etiq    = {}
        counter = [0]
        raiz    = self._agregar_nodos(grafo, etiq, arbol, None, counter)

        pos = self._posiciones(grafo, raiz)

        plt.figure(figsize=(11, 7))
        nx.draw(
            grafo, pos,
            labels=etiq,
            with_labels=True,
            node_size=1800,
            node_color="#3b82c4",
            font_color="white",
            font_size=10,
            arrows=False,
        )
        plt.title(titulo, fontsize=13, fontweight="bold")
        plt.tight_layout()
        plt.show(block=False)   # no bloquea la ventana principal
        plt.pause(0.1)

    def _agregar_nodos(self, grafo, etiq, arbol, padre, counter):
        nid = counter[0]
        counter[0] += 1
        etiq[nid] = arbol.label() if isinstance(arbol, Tree) else str(arbol)
        grafo.add_node(nid)
        if padre is not None:
            grafo.add_edge(padre, nid)
        if isinstance(arbol, Tree):
            for hijo in arbol:
                self._agregar_nodos(grafo, etiq, hijo, nid, counter)
        return nid

    def _posiciones(self, grafo, raiz, ancho=1.0, gap=0.2, y=0.0, cx=0.5):
        """Calcula posiciones jerárquicas de forma recursiva."""
        hijos = list(grafo.successors(raiz))
        pos   = {raiz: (cx, y)}
        if hijos:
            dx     = ancho / len(hijos)
            x_hijo = cx - ancho / 2 + dx / 2
            for hijo in hijos:
                pos.update(self._posiciones(grafo, hijo, dx, gap, y - gap, x_hijo))
                x_hijo += dx
        return pos


# ─────────────────────────────────────────────────────────────────────────── #
# Interfaz gráfica principal (Tkinter)                                        #
# ─────────────────────────────────────────────────────────────────────────── #

class Aplicacion:
    """Ventana principal de la aplicación."""

    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.raiz.title("Generador de Derivación, Árbol de Derivación y AST")
        self.raiz.geometry("950x720")

        # Estado
        self.arbol_derivacion: Tree | None = None
        self.arbol_ast:        Tree | None = None
        self.visualizador = VisualizadorArbol()

        self._crear_widgets()

    # ── Construcción de la UI ─────────────────────────────────────────── #

    def _crear_widgets(self):
        marco = ttk.Frame(self.raiz, padding=10)
        marco.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(
            marco,
            text="Generador de Árbol de Derivación y AST\npara Gramáticas Libres de Contexto",
            font=("Arial", 13, "bold"),
            justify="center",
        ).pack(pady=(0, 8))

        # ── Panel entrada ──────────────────────────────────────────────── #
        entrada = ttk.LabelFrame(marco, text="Entrada", padding=10)
        entrada.pack(fill=tk.X, pady=4)

        ttk.Label(entrada, text="Gramática CFG:").pack(anchor="w")
        self.campo_gram = tk.Text(entrada, height=7, font=("Courier New", 10))
        self.campo_gram.pack(fill=tk.X)
        self.campo_gram.insert(tk.END, GRAMATICA_DEFAULT)

        ttk.Label(
            entrada,
            text="Expresión objetivo, separada por espacios:",
        ).pack(anchor="w", pady=(8, 0))
        self.campo_expr = ttk.Entry(entrada, font=("Courier New", 11))
        self.campo_expr.pack(fill=tk.X)
        self.campo_expr.insert(0, EXPRESION_DEFAULT)
        self.campo_expr.bind("<Return>", lambda _: self.generar())

        ttk.Label(
            entrada,
            text="Ejemplos válidos:  4 + 5  |  x - y / 2  |  total * 3 + edad  |  ( 4 + x ) / 2",
            foreground="gray",
        ).pack(anchor="w", pady=(3, 0))

        # Controles (radios + botones en una fila)
        ctrl = ttk.Frame(entrada)
        ctrl.pack(fill=tk.X, pady=8)

        self.tipo = tk.StringVar(value="izquierda")
        ttk.Radiobutton(ctrl, text="Derivación por la izquierda",
                        variable=self.tipo, value="izquierda").pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(ctrl, text="Derivación por la derecha",
                        variable=self.tipo, value="derecha").pack(side=tk.LEFT, padx=4)

        ttk.Button(ctrl, text="Generar",
                   command=self.generar).pack(side=tk.LEFT, padx=12)
        ttk.Button(ctrl, text="Ver árbol de derivación",
                   command=self.ver_arbol).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text="Ver AST",
                   command=self.ver_ast).pack(side=tk.LEFT, padx=4)

        # ── Panel salida ───────────────────────────────────────────────── #
        salida = ttk.LabelFrame(marco, text="Salida", padding=10)
        salida.pack(fill=tk.BOTH, expand=True, pady=4)

        scroll = ttk.Scrollbar(salida)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.texto = tk.Text(salida, font=("Courier New", 10),
                             yscrollcommand=scroll.set)
        self.texto.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.texto.yview)

    # ── Acciones ──────────────────────────────────────────────────────── #

    def generar(self):
        """Analiza la expresión y muestra la derivación y árboles en texto."""
        try:
            texto_gram = self.campo_gram.get("1.0", tk.END).strip()
            expresion  = self.campo_expr.get().strip()

            if not texto_gram or not expresion:
                messagebox.showwarning("Advertencia", "Completa la gramática y la expresión.")
                return

            modelo = ModeloGramatica(texto_gram)
            self.arbol_derivacion, tokens = modelo.parsear(expresion)

            if self.arbol_derivacion is None:
                messagebox.showerror("Error",
                    "La expresión no pertenece a la gramática ingresada.\n"
                    "Verifica que los tokens coincidan con los terminales de la gramática.")
                return

            izquierda = self.tipo.get() == "izquierda"
            pasos     = GeneradorDerivacion(self.arbol_derivacion).derivar(izquierda)
            self.arbol_ast = GeneradorAST().generar(self.arbol_derivacion)

            # Formatear salida
            dir_label = "Derivación por la izquierda" if izquierda else "Derivación por la derecha"
            flecha    = "⇒I" if izquierda else "⇒D"

            self.texto.delete("1.0", tk.END)
            self._escribir(dir_label)
            self._escribir("=" * 60 + "\n")
            self._escribir(f"Expresión ingresada:\n{expresion}\n")
            self._escribir(f"Tokens reconocidos por la gramática:\n{' '.join(tokens)}\n")
            self._escribir("Pasos de derivación:")
            for i, paso in enumerate(pasos, start=1):
                self._escribir(f"  Paso {i}: {paso}")
            self._escribir(f"\nÁrbol de derivación en formato texto:\n{self.arbol_derivacion}")
            self._escribir(f"\nÁrbol de Sintaxis Abstracta (AST) en formato texto:\n{self.arbol_ast}")

            messagebox.showinfo("Listo", "Derivación, árbol y AST generados correctamente.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ver_arbol(self):
        """Muestra el árbol de derivación en una ventana Matplotlib."""
        if self.arbol_derivacion is None:
            messagebox.showwarning("Advertencia", "Primero presiona 'Generar'.")
            return
        self.visualizador.mostrar(self.arbol_derivacion, "Árbol de Derivación")

    def ver_ast(self):
        """Muestra el AST en una ventana Matplotlib."""
        if self.arbol_ast is None:
            messagebox.showwarning("Advertencia", "Primero presiona 'Generar'.")
            return
        self.visualizador.mostrar(self.arbol_ast, "Árbol de Sintaxis Abstracta (AST)")

    def _escribir(self, texto: str):
        self.texto.insert(tk.END, texto + "\n")


# ─────────────────────────────────────────────────────────────────────────── #
# Punto de entrada                                                             #
# ─────────────────────────────────────────────────────────────────────────── #

if __name__ == "__main__":
    raiz = tk.Tk()
    Aplicacion(raiz)
    raiz.mainloop()
