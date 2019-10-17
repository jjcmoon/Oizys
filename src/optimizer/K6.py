import grammar.kg as kg
from util.SLIDE_solver import diff_solver, eq_solver
from codegen.util import *

import sympy as sp
import numpy as np

from typing import Set, Tuple


def smoothen(kprog: kg.KLoop) -> Tuple[kg.KLoop, Set[int], bool]:
    spt = 0
    toks = []
    names = set()

    for tok in kprog.content.body:
        if isinstance(tok, kg.KTapeSet):
            tok = kg.KTapeSet(tok.offs+spt, spexpr_shift(tok.expr, spt))
            toks.append(tok)
            names |= spexpr_access(tok.expr)
            names.add(tok.offs)
        elif isinstance(tok, kg.KTapeAdjust):
            tok = kg.KTapeAdjust(tok.offs + spt, spexpr_shift(tok.expr, spt))
            toks.append(tok)
            names |= spexpr_access(tok.expr)
            names.add(tok.offs)
        elif isinstance(tok, kg.KTapeMove):
            spt += tok.delta
        elif isinstance(tok, kg.KOutput):
            tok = kg.KOutput(tok.offs+spt)
            toks.append(tok)
        elif isinstance(tok, kg.KInput):
            tok = kg.KInput(tok.offs+spt)
            toks.append(tok)
        else:
            raise NotImplementedError()

    balanced = spt == 0
    if not balanced:
        toks.append(kg.KTapeMove(spt))

    return kg.KLoop(kg.KProgram(toks)), names, balanced


def K2M(kprog: kg.KLoop, names: Set[int]):
    names = sorted(list(names), key=lambda x: abs(x))
    N = len(names)
    if names[0] != 0:
        print("Loop without stepping detected")
    names = {name: i for (i, name) in enumerate(names)}

    A = np.eye(N, dtype=int)
    B = np.zeros((N, 1), dtype=int)

    def construct_row(expr):
        row = np.zeros((1, N), dtype=int)
        cnst = 0

        if type(expr) == int or type(expr) == sp.Integer:
            cnst += expr
        elif expr.func == sp.Add:
            lhs, rhs = expr.args
            rlhs, clhs = construct_row(lhs)
            rrhs, crhs = construct_row(rhs)
            row = row + rlhs + rrhs
            cnst += clhs + crhs
        elif expr.func == sp.Mul:
            lhs, rhs = expr.args
            assert type(lhs) == sp.Integer
            assert rhs.is_symbol

            idd = int(str(rhs)[3:])
            ss = names[idd]
            amm = lhs*A[ss, :]
            row = row + amm
        elif expr.is_symbol:
            idd = int(str(expr)[3:])
            ss = names[idd]
            row += A[ss, :]
            cnst += B[ss]

        return row.squeeze(), cnst

    for tok in kprog.content.body:
        if isinstance(tok, kg.KTapeSet):
            r = names[tok.offs]
            row, cnst = construct_row(tok.expr)
            B[r] = cnst
            A[r, :] = row

        elif isinstance(tok, kg.KTapeAdjust):
            r = names[tok.offs]
            row, cnst = construct_row(tok.expr)
            B[r] += cnst
            A[:, r] += row
        else:
            raise RuntimeError("unsupported tok" + str(tok))

    A = A%256
    B = B%256

    return A, B, names


def M2K(R, S, names):
    n = R.shape[0]
    names = flip_dict(names)
    toks = []
    vars = sp.Matrix([tape_spvar(names[t]) for t in range(n)])

    cond, tlc = eq_solver(R, S)
    if cond == False:
        tlc_var = tlc
    else:
        tlc_id = fresh_varid()
        toks.append(kg.KVarSet(tlc_id, tlc))
        tlc_var = cns_spvar(tlc_id)

    def destruct_row(row, cnst):
        r = row @ vars
        tot = sp.simplify((r[0, 0] + cnst) % 256)
        if tot.func == sp.Mod:
            tot = tot.args[0]
        return tot

    def first_nonzero(a):
        r = R.row(a)
        for i in range(n):
            if r[i] != 0:
                return i
        return n

    covered = sorted(list(range(n)), key=lambda x: first_nonzero(x))
    for j in range(n):
        i = covered[j]
        offs = names[i]
        if offs == 0:
            continue
        expr = destruct_row(R.row(i), S.row(i)[0])
        expr = expr.subs(sp.Symbol('n', positive=True, integer=True), tlc_var)
        toks.append(kg.KTapeSet(offs, sp.simplify(expr)))

    if cond != False:
        cond_tok = kg.KIf(cond, kg.KInfLoop())
        toks = [cond_tok] + toks

    toks.append(kg.KTapeSet(0, 0))
    return kg.KProgram(toks)


def convert(kloop: kg.KLoop) -> Tuple[kg.KProgram, int]:
    assert not kloop.is_deep()
    if kloop.is_simple():
        kloop, names, balanced = smoothen(kloop)
        if balanced:
            try:
                A, B, names = K2M(kloop, names)
                R, S = diff_solver(A, B)
                return M2K(R, S, names), 1
            except:
                pass
    return kg.KProgram([kloop]), 2


def deeper_convert(kloop: kg.KLoop) -> Tuple[kg.KProgram, int]:
    ntokens = []
    mdepth = 0
    for tok in kloop.content.body:
        if isinstance(tok, kg.KLoop):
            if kloop.is_deep():
                rconv, succ = deeper_convert(tok)
            else:
                rconv, succ = convert(tok)
            mdepth = max(mdepth, succ)
            ntokens += rconv.body
        else:
            ntokens.append(tok)

    nloop = kg.KLoop(kg.KProgram(ntokens))
    if nloop.is_simple() and not nloop.is_deep() and mdepth < 2:
        res, success = convert(nloop)
        if not success:
            return res, 2
        elif success and mdepth == 1:
            return kg.KProgram([kg.KIf(sp.Ne(tape_spvar(0),0), res)]), 2
        elif success and mdepth == 0:
            return res, 1
    else:
        return kg.KProgram([nloop]), 2


def lift_convert(kprogram):
    r = []
    for tok in kprogram.body:
        if isinstance(tok, kg.KLoop):
            ts, d = deeper_convert(tok)
            if (d==2):
                print("HIGH DEPTH")
            r += ts.body
        else:
            r.append(tok)
    return kg.KProgram(r)


def flip_dict(d):
    return {v: k for (k, v) in d.items()}
