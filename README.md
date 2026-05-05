# Práctica III – Generador de Árbol de Derivación y AST para GLC

**Curso:** ST0244 – Lenguajes de Programación y Paradigmas de Computación  
**Universidad:** Universidad EAFIT – Escuela de Ciencias Aplicadas e Ingeniería  
**Docente:** Alexander Narváez Berrío

---

## Integrantes

| Nombre completo | 
|-----------------|
| Juan David Giraldo Regino |
| Juan José Duque Marín |

---

## Descripción

Aplicación con interfaz gráfica que, dada una **Gramática Libre de Contexto (GLC)** y una **expresión objetivo**, genera:

1. **Derivación** — secuencia de formas sentenciales usando expansión por izquierda o por derecha.
2. **Árbol de derivación** — representación visual de cada paso de expansión de la gramática.
3. **AST (Árbol de Sintaxis Abstracta)** — árbol simplificado que elimina nodos redundantes y resalta la estructura esencial de la expresión.

---

## Tecnología

| Elemento | Detalle |
|----------|---------|
| Lenguaje | Python 3.10+ |
| Interfaz gráfica | Tkinter (incluido en Python) |
| Gramática / análisis | NLTK 3.9 — CFG + EarleyChartParser |
| Visualización de árboles | matplotlib 3.10 + networkx 3.5 |
| IDE | VS Code |

---

## Instalación y ejecución

```bash
# 1. Instalar dependencias
pip install nltk matplotlib networkx

# 2. Ejecutar la aplicación
python practica_glc.py
```

---

## Formato de la gramática

La gramática se escribe en notación BNF de NLTK. Los terminales van entre comillas simples:

```
S -> E
E -> E '+' T | E '-' T | T
T -> T '*' F | T '/' F | F
F -> '(' E ')' | 'num' | 'id'
```

La expresión se ingresa con **tokens separados por espacios**.  
Los números (`4`, `3.14`) se normalizan a `num` y las variables (`x`, `edad`) a `id` automáticamente.

---

## Arquitectura OOP — archivo único `practica_glc.py`

| Clase | Responsabilidad |
|-------|----------------|
| `ModeloGramatica` | Carga el CFG, tokeniza y analiza la expresión |
| `GeneradorDerivacion` | Produce los pasos de derivación izquierda o derecha |
| `GeneradorAST` | Simplifica el árbol de derivación en un AST |
| `VisualizadorArbol` | Dibuja árboles con NetworkX y Matplotlib |
| `Aplicacion` | Ventana principal Tkinter, orquesta todos los módulos |

---

## Criterios de evaluación

| Criterio | Peso |
|----------|------|
| Solución OOP con todas las funcionalidades | 70 % |
| Sustentación presencial | 30 % |
