# CFG Derivation Tree & AST Generator — Practice III

**Course:** ST0244 – Programming Languages and Computing Paradigms  
**University:** EAFIT University — School of Applied Sciences and Engineering  
**Lecturer:** Alexander Narváez Berrío

---

## Team Members

| Name | Student ID |
|------|-----------|
| Juan David García Narváez | (your ID here) |

---

## Project Description

A GUI application that, given a **Context-Free Grammar (CFG)** and a **target expression**, produces:

1. **Derivation** — step-by-step sentential forms using *left* or *right* expansion.  
2. **Derivation Tree** — visual parse tree representing every grammar expansion.  
3. **Abstract Syntax Tree (AST)** — simplified tree that collapses chain rules and  
   highlights the essential syntactic structure.

---

## Technology Stack

| Item | Detail |
|------|--------|
| Language | Python 3.10+ |
| GUI framework | PyQt5 5.15 |
| Grammar / parsing | NLTK 3.8 (CFG + EarleyChartParser) |
| IDE | VS Code / PyCharm |

---

## Architecture (OOP)

```
main.py              – entry point
grammar.py           – Grammar class  (wraps NLTK CFG)
parser_engine.py     – ParserEngine class  (wraps EarleyChartParser)
derivation.py        – Derivation class  (left/right derivation steps)
ast_builder.py       – ASTBuilder class  (parse tree → AST)
tree_layout.py       – LayoutNode, compute_layout  (2-D tree positioning)
tree_widget.py       – TreeCanvas, TreeWidget  (PyQt5 custom painting)
main_window.py       – MainWindow  (main GUI, orchestration)
```

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the application
python main.py
```

---

## Grammar Format

The grammar must be written in NLTK's BNF notation:

```
S -> NP VP
NP -> Det N | N
VP -> V NP | V
Det -> 'the' | 'a'
N -> 'dog' | 'cat'
V -> 'chased' | 'saw'
```

Terminals must be **quoted** (single quotes).  
The expression is entered as **space-separated tokens** that match the quoted terminals.

---

## Features

- **Left derivation** — always expands the leftmost non-terminal.  
- **Right derivation** — always expands the rightmost non-terminal.  
- **Scrollable tree canvases** for large grammars.  
- **Three example presets** (natural language, arithmetic, aⁿbⁿ).  
- Supports **left-recursive grammars** (e.g. arithmetic) via Earley parsing.

---

## Assessment Criteria

| Criterion | Weight |
|-----------|--------|
| OOP solution with all features working | 70 % |
| In-person defence | 30 % |
