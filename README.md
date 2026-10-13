# Proyecto 2: Algoritmo CYK y simplificación de gramáticas

Teoría de la Computación

## Integrantes

- Josue Hernández
- Juan Daniel Ordóñez
- José Sánchez

## Video

Enlace al video: (pegar aquí el enlace)

## Descripción

El programa decide si una frase en inglés pertenece al lenguaje de una gramática
libre de contexto. Como el algoritmo CYK solo funciona con gramáticas en Forma
Normal de Chomsky (CNF), primero se simplifica la gramática y se convierte a CNF:

```
archivo -> sin ε -> sin unarias -> sin inútiles -> CNF -> CYK -> parse tree
```

La salida es SÍ o NO, el tiempo que tardó CYK y, si la frase se acepta, su parse
tree. La gramática por defecto es la del enunciado, pero el programa lee
cualquier gramática desde un archivo de texto.

## Requisitos

Python 3.9 o superior. No usa librerías externas.

```bash
git clone git@github.com:her24770/teoria_compu-project-2.git
cd teoria_compu-project-2
```

## Uso

```bash
python3 main.py                                   # pregunta la frase
python3 main.py "She eats a cake with a fork"     # gramática en inglés por defecto
python3 main.py --steps "the cat drinks the beer" # muestra la gramática en cada etapa
python3 main.py -g grammars/1.txt "( id * id ) + id"
```

Opciones:

- `-g archivo`: gramática a usar (por defecto `grammars/english.txt`).
- `--steps`: imprime la gramática original, la simplificada y la CNF antes de
  validar la frase.

En las gramáticas aritméticas la frase se escribe con los símbolos separados por
espacios. Ejemplo de salida:

```
$ python3 main.py "she eats a cake with a fork"
Frase: she eats a cake with a fork
Resultado: SÍ
Tiempo de CYK: 0.0227 ms

Parse tree:
S
├── NP
│   └── she
└── VP
    ├── VP
    │   ├── V
    │   │   └── eats
    │   └── NP
    │       ├── Det
    │       │   └── a
    │       └── N
    │           └── cake
    └── PP
        ├── P
        │   └── with
        └── NP
            ├── Det
            │   └── a
            └── N
                └── fork
```

Si la frase no pertenece al lenguaje, el resultado es `NO` y se indican las
palabras que no están en la gramática.

## Pruebas

```bash
python3 -m unittest discover -s tests -t . -v
```

Son 89 pruebas: lector de gramáticas, cada paso de simplificación, conversión a
CNF, CYK y ejecución completa de `main.py`.

## Formato de las gramáticas

Una regla por línea, símbolos separados por espacios, alternativas con `|` y `e`
para la cadena vacía. La primera regla define el símbolo inicial. Ejemplo
(`grammars/1.txt`):

```
E -> T X
X -> + T X | e
T -> F Y
Y -> * F Y | e
F -> ( E ) | id
```

Todo símbolo que aparece a la izquierda de una regla es una variable; el resto
son terminales.

## Estructura del proyecto

| Archivo | Función |
|---|---|
| `grammar.py` | Modelo de la gramática y lector de archivos |
| `epsilon.py` | Eliminación de ε-producciones |
| `unit.py` | Eliminación de producciones unarias |
| `useless.py` | Eliminación de símbolos inútiles |
| `cnf.py` | Conversión a Forma Normal de Chomsky |
| `simplify.py` | Encadena los pasos anteriores |
| `cyk.py` | Algoritmo CYK y construcción del parse tree |
| `main.py` | Programa principal |
| `demo_p1.py`, `demo_p2.py` | Muestran paso a paso la simplificación y la CNF |
| `grammars/` | Gramáticas de ejemplo (`english.txt`, `1.txt`, `1-cnf.txt`) |
| `tests/` | Pruebas automáticas |
| `docs/` | Documentación |

## Documentación

El informe completo está en [`docs/Documentacion.pdf`](docs/Documentacion.pdf)
(fuente en [`docs/DOCUMENTACION.md`](docs/DOCUMENTACION.md)). Incluye el diseño,
los algoritmos, ejemplos, pruebas y la discusión.
