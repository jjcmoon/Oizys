import grammar.bfg as bfg
import parsy


def _yield_parser(s, out):
    @parsy.generate
    def wrapper():
        yield parsy.string(s)
        return out
    return wrapper


def parse(program):
    # TODO: cleaning after parsing (better error reporting)?
    clean = "".join(filter(lambda x: x in bfg.TOKENS, list(program)))

    plus = _yield_parser("+", bfg.Plus())
    minus = _yield_parser("-", bfg.Minus())
    left = _yield_parser("<", bfg.Left())
    right = _yield_parser(">", bfg.Right())
    input = _yield_parser(",", bfg.Input())
    output = _yield_parser(".", bfg.Output())

    @parsy.generate
    def loop():
        yield parsy.string("[")
        contents = yield bf
        yield parsy.string("]")
        return bfg.Loop(bfg.BfProgram(contents))

    tok = plus | minus | left | right | input | output | loop
    bf = tok.many()
    return bfg.BfProgram(bf.parse(clean))
