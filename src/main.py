import subprocess
import click

import parser.parser as parser
import optimizer.K4 as K4
import optimizer.K6 as K6
from codegen.cgen import c_gen
from codegen.pygen import py_gen


def run_cmd(cmd):
    subprocess.call(cmd.split(" "))


@click.command()
@click.argument('filename')
@click.option('-O1', 'opt_flag', flag_value='quick')
@click.option('-O2', 'opt_flag', flag_value='hard', default=True)
@click.option('--code_gen', default='c', help='target language')
@click.option('-o', default='test', help='output filename')
def main(filename, opt_flag, code_gen, o):
    # open bf code
    print(opt_flag)
    
    with open(filename, 'r') as f:
        bf = f.read()

    # parser
    parsed = parser.parse(bf)

    # optimizer
    print("## 4PASS ###")
    opt = K4.lift_convert(parsed)
    print(opt)

    if opt_flag == 'hard':
        print("### 6PASS ###")
        opt = K6.lift_convert(opt)
        print(opt)

    # code generation
    print("### CODEGEN ###")

    if code_gen == 'py':
        py_code = "\n".join(py_gen(opt))
        with open(f"{o}.py", "w+") as f:
            f.write(py_code)

    elif code_gen == 'c':
        c_code = '\n'.join(c_gen(opt))
        with open(f"{o}.c", "w+") as f:
            f.write(c_code)
        run_cmd(f'gcc -O2 {o}.c -o {o}')

    else:
        Exception("Illegal codegen type")


if __name__ == '__main__':
    main()