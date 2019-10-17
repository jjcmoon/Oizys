import attr
from codegen.cgen import c_gen_sp, c_arr
from codegen.pygen import py_gen_sp, py_arr
from codegen.util import indent
from functools import reduce

#TODO: refactor to visitor?
@attr.s
class KProgram:
    body = attr.ib()

    def c_gen(self):
        # TODO: best way to flatmap in python?
        res = list(map(lambda x: x.c_gen(), self.body))
        if len(self.body) == 0:
            return []
        return reduce(list.__add__, res)

    def py_gen(self):
        res = list(map(lambda x: x.py_gen(), self.body))
        if len(self.body) == 0:
            return []
        return reduce(list.__add__, res)




@attr.s
class KTapeSet:
    offs = attr.ib()
    expr = attr.ib()

    def c_gen(self):
        return [f"{c_arr(self.offs)} = {c_gen_sp(self.expr)};"]

    def py_gen(self):
        return [f"{py_arr(self.offs)} = {py_gen_sp(self.expr)}"]



@attr.s
class KTapeAdjust:
    offs = attr.ib()
    expr = attr.ib()

    def c_gen(self):
        return [f"{c_arr(self.offs)} += {c_gen_sp(self.expr)};"]

    def py_gen(self):
        return [f"{py_arr(self.offs)} += {py_gen_sp(self.expr)}"]


@attr.s
class KTapeMove:
    delta = attr.ib()

    def c_gen(self):
        return [f"sp += {self.delta};"]

    def py_gen(self):
        return [f"sp += {self.delta}"]

@attr.s
class KVarSet:
    idx = attr.ib()
    expr = attr.ib()


@attr.s
class KIf:
    cond = attr.ib()
    then = attr.ib(type=KProgram)

    def c_gen(self):
        return \
            [f"if ({c_gen_sp(self.cond)}) {{"] + \
            indent(self.then.c_gen()) + \
            ["}"]

    def py_gen(self):
        return \
            [f"if {c_gen_sp(self.cond)}:"] + \
            indent(self.then.py_gen())


@attr.s
class KLoop:
    content = attr.ib(type=KProgram)

    def c_gen(self):
        return \
            ["while (arr[sp]) {"] + \
            indent(self.content.c_gen()) + \
            ["}"]

    def py_gen(self):
        return \
            ["while arr[sp]:"] + \
            (indent(self.content.py_gen())
                if len(self.content.body) > 0 else ['\tpass'])

    def is_simple(self):
        sp = 0
        for tok in self.content.body:
            if isinstance(tok, KLoop) and not tok.is_simple():
                return False
            if isinstance(tok, KIf):
                return False
            if isinstance(tok, KTapeMove):
                sp += tok.delta
        return sp == 0

    def is_deep(self):
        return any(isinstance(tok, KLoop) for tok in self.content.body)




@attr.s
class KInfLoop:
    def c_gen(self):
        return ["while (1) {}"]

    def py_gen(self):
        return ['while True: pass']


@attr.s
class KOutput:
    offs = attr.ib()

    def c_gen(self):
        return [f"putchar({c_arr(self.offs)});"]

    def py_gen(self):
        return [f"print_chr({py_arr(self.offs)})"]


@attr.s
class KInput:
    offs = attr.ib()

    def c_gen(self):
        return [f"{c_arr(self.offs)} = getchar();"]

    def py_gen(self):
        return [f"{py_arr(self.offs)} = ord(input())"]


