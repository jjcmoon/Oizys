# Oizys
Inspired by projects like Esotope-bfc and Tritium, Oizys is a highly optimizing compiler for brainfuck.
Unlike the previously mentioned projects however, Oizys is not composed of a great amount of adhoc optimizations. Instead a novel algorithm was developed: K6, which is much more general, and can optimize a new class of programs (deep balanced loops).

Oizys is still under developement, and still contains bugs.

The compiler is named after Oizys, the primordial greek goddess of Misery. Her latin name is Miseria, from which the english misery is derived. She is the daughter of Nyx, goddess of the night, and the twin of Momus, god of satire and mockery.

## Usage

Oizys requires python3. Make sure to have installed the following libraries:

```
pip install click, numpy, sympy, parsy
```

Now Oizys can compile a bf program with:

```
python3 src/main.py helloworld.bf -o hello
```

This will output a `hello.c` file (the default backend is C, but Python is also supported). As well as a executable (compiled with `gcc -O2`).


## Brainfuck Semantics

The compiler assumes a tape of length 30000 cells, each a unsigned byte (overflow allowed). Accessing cells outside of the tape is undefined behaviour (using the C backend, this will segfault, python has a cyclical tape). 

A configurable cell/tape size might be added later on.
