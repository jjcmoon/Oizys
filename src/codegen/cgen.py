from sympy.printing.ccode import C99CodePrinter
from codegen.util import indent


class CPrinter(C99CodePrinter):
    def _print_Symbol(self, expr):
        if expr.name[:3] == 'var':
            offs = int(expr.name[3:])
            return c_arr(offs)
        return super(CPrinter, self)._print_Symbol(expr)

    def _print_Integer(self, expr):
        if expr.p == 256:
            return "256"
        return str(expr.p % 256)

    def _print_Mod(self, expr):
        lhs, rhs = expr.args
        return f"({self.doprint(lhs)}) % {self.doprint(rhs)}"


def c_gen_sp(expr):
    return CPrinter().doprint(expr)


def c_header():
    return ["#include <stdio.h>",
            "char arr[30000]={0};",
            "int sp=0;"] + \
            c_pow() + \
            ["int main() {"]


def c_arr(offs):
    if offs == 0:
        return 'arr[sp]'
    elif offs < 0:
        return f"arr[sp{offs}]"
    else:
        return f"arr[sp+{offs}]"


def c_footer():
    return ["\treturn 0;", "}"]


def c_pow():
    return """
char pow(char base, char exp) {
    char result = 1;
    for (;;)
    {
        if (exp & 1)
            result *= base;
        exp >>= 1;
        if (!exp)
            break;
        base *= base;
    }
    return result;
}
""".split('\n')


def c_gen(program):
    return c_header() + indent(program.c_gen()) + c_footer()
