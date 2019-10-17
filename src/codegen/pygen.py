from sympy.printing.python import PythonPrinter
from codegen.util import indent


class PyPrinter(PythonPrinter):
    def _print_Symbol(self, expr):
        if expr.name[:3] == 'var':
            offs = int(expr.name[3:])
            return py_arr(offs)
        return super(PyPrinter, self)._print_Symbol(expr)

    def _print_Integer(self, expr):
        if expr.p == 256:
            return "256"
        return str(expr.p % 256)

    def _print_Mod(self, expr):
        lhs, rhs = expr.args
        return f"({self.doprint(lhs)}) % {self.doprint(rhs)}"


def py_gen_sp(expr):
    return PyPrinter().doprint(expr)


def py_header():
    return [
        "import numpy as np\n",
        "def print_chr(c):",
        "\tprint(chr(c), end='', flush=True)",
        "",
        "def main():",
            "\tarr = np.zeros(30000, dtype=np.ubyte)",
            "\tsp=0"]


def py_arr(offs):
    if offs == 0:
        return 'arr[sp]'
    elif offs < 0:
        return f"arr[sp{offs}]"
    else:
        return f"arr[sp+{offs}]"


def py_footer():
    return ["", "main()"]




def py_gen(program):
    return py_header() + indent(program.py_gen()) + py_footer()
