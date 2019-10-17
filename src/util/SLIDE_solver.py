import sympy as sp
import numpy as np
from math import gcd

from codegen.util import tape_spvar, is_int_like

# Symbolic SOLDEWIC solver
# SOLDEWIC = System Of Linear Difference Equations With Integer Constants


def diff_solver(A, B):
    A = sp.Matrix(A)
    B = sp.Matrix(B)
    P, D = A.diagonalize()

    n = sp.symbols('n', positive=True, integer=True)
    N = A.shape[0]
    for i in range(N):
        D[i, i] = D[i, i] ** n

    R = P * D * (P ** -1)
    S = summa_aux(R * B, n)
    for i in range(N):
        assert S[i].is_integer
        for j in range(N):
            assert R[i, j].is_integer
    return R, S


def summa_aux(expr, t):
    if type(expr) == sp.Matrix:
        l = lambda x: summa_aux(x, t)
        return expr.applyfunc(l)
    if expr.is_integer:
        return t * expr
    if expr.func == sp.Add:
        lhs, rhs = expr.args
        return summa_aux(lhs, t) + summa_aux(rhs, t)
    if expr.func == sp.Pow:
        base, expo = expr.args
        assert base.is_integer
        return (1 - base ** t) / (1 - base)
    raise RuntimeError("%s not found" % expr)


def egcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = egcd(b % a, a)
        return g, x - (b // a) * y, y


def mod_inv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


CS = 256
def eq_solver(A, B):
    A = np.array(A)
    tgv = tape_spvar(0)

    if np.all(A[:, 0] == np.zeros(A.shape)[:, 0]):
        cond = False
        k = 1
        return cond, k
    elif np.any(A[:, 0] != np.eye(A.shape[0])[:, 0]):
        raise Exception("Not solvable")
    try:
        sdict = B[0].as_coefficients_dict()
        assert len(sdict) == 1
        S = -tuple(sdict.values())[0] % CS
    except:
        raise Exception("Not solvable")

    g = gcd(CS, S)
    p = mod_inv(S // g, CS // g)
    cond = sp.simplify(sp.Ne(tgv % g, 0))

    if g!= 1:
        k = (tgv/g*p) % CS//g
    else:
        k = tgv/g*p

    # TODO: also allow bit shift division
    assert (tgv/g*p).is_integer
    return cond, k
