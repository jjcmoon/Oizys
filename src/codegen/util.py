import sympy as sp
import numpy as np

"""
Provides the freshest variables
"""

var_counter = 0


def fresh_varid():
    global var_counter
    t = var_counter
    var_counter += 1
    return t


def tape_spvar(offs):
    return sp.Symbol(f"var{offs}", integer=True)


def cns_spvar(idd):
    return sp.Symbol(f"cns{idd}", integer=True)


def fresh_spvar():
    return cns_spvar(fresh_varid())


def indent(l):
    return ["\t"+x for x in l]


def is_int_like(n):
    if type(n) == sp.Matrix:
        M = np.array(n)
        return np.all(is_int_like(x) for x in M)
    #return type(n) == int or type(n) == sp.Integer or n.has(sp.Integral)
    return type(n) in (int, sp.Integer, sp.numbers.Zero, sp.numbers.One, sp.numbers.NegativeOne)


def spexpr_shift(expr, offs):
    if is_int_like(expr):
        return expr
    if type(expr) == sp.Symbol:
        name = expr.name[:3]
        pos = int(expr.name[3:])
        assert(name == 'var')
        return tape_spvar(pos+offs)

    lhs = spexpr_shift(expr.args[0], offs)
    rhs = spexpr_shift(expr.args[1], offs)
    if type(expr) == sp.Add:
        return lhs+rhs
    if type(expr) == sp.Mul:
        return lhs*rhs
    if type(expr) == sp.Pow:
        return lhs**rhs
    raise NotImplementedError()


def spexpr_access(expr):
    if is_int_like(expr):
        return set()
    if type(expr) == sp.Symbol:
        pos = int(expr.name[3:])
        assert(expr.name[:3] == 'var')
        return {pos}

    lhs = spexpr_access(expr.args[0])
    rhs = spexpr_access(expr.args[1])
    return lhs.union(rhs)
