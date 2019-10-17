import grammar.bfg as bfg
import grammar.kg as kg


def convert(bf: bfg.BfProgram):
    tape = {}
    sp = 0

    tokens = []

    def tape_get(ind):
        if ind in tape:
            return tape[ind]
        else:
            return 0

    for tok in bf.body:
        if tok == bfg.Plus():
            tape[sp] = tape_get(sp) + 1
        elif tok == bfg.Minus():
            tape[sp] = tape_get(sp) - 1

        elif tok == bfg.Left():
            sp += -1
        elif tok == bfg.Right():
            sp += 1

        elif tok == bfg.Output():
            if sp in tape:
                tokens.append(kg.KTapeAdjust(sp, tape[sp]))
            tokens.append(kg.KOutput(sp))
            tape[sp] = 0

        elif tok == bfg.Input():
            tokens.append(kg.KInput(sp))
            tape[sp] = 0

        else:
            RuntimeError("Wrong token")

    for (offs, val) in sorted(tape.items()):
        if val == 0:
            continue
        tokens.append(kg.KTapeAdjust(offs, val))

    if sp != 0:
        tokens.append(kg.KTapeMove(sp))

    return tokens


def lift_convert(bf):
    acc = []
    res = []
    for tok in bf.body:
        if isinstance(tok, bfg.Loop):
            res += convert(bfg.BfProgram(acc))
            acc = []
            res.append(kg.KLoop(lift_convert(tok.body)))
        else:
            acc.append(tok)
    res += convert(bfg.BfProgram(acc))
    return kg.KProgram(res)

