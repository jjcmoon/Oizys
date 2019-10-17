import attr


TOKENS = "+", "-", "<", ">", ".", ",", "[", "]"


@attr.s
class BfProgram:
    body = attr.ib()

    def __str__(self):
        return "".join(str(x) for x in self.body)


@attr.s
class Plus:
    def __str__(self):
        return "+"


@attr.s
class Minus:
    def __str__(self):
        return "-"


@attr.s
class Left:
    def __str__(self):
        return "<"


@attr.s
class Right:
    def __str__(self):
        return ">"


@attr.s
class Input:
    def __str__(self):
        return ","


@attr.s
class Output:
    def __str__(self):
        return "."


@attr.s
class Loop:
    body = attr.ib(type=BfProgram)

    def __str__(self):
        return f"[{str(self.body)}]"

