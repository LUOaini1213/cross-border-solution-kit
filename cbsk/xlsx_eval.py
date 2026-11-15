"""A small, independent evaluator for the formulas the kit writes into its workbooks.

It reads formulas back from the saved .xlsx (openpyxl does not calculate) and evaluates them, so tests
can check that the workbook's live totals equal the Python totals. Supported: numbers, strings, cell
references with optional sheet prefix and $ anchors, ranges inside functions, + - * / ^, unary minus,
comparisons (= <> < > <= >=) and SUM, MAX, MIN, AVERAGE, COUNT, ROUND, ABS, IF.
Anything else raises, so an unsupported formula cannot pass silently.
"""
from __future__ import annotations

import re
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string, get_column_letter

TOKEN = re.compile(r"""
    (?P<ws>\s+)
  | (?P<num>\d+(\.\d*)?([eE][+-]?\d+)?|\.\d+([eE][+-]?\d+)?)
  | (?P<str>"([^"]|"")*")
  | (?P<ref>(('[^']+'|[A-Za-z_][A-Za-z0-9_\.]*)!)?\$?[A-Z]{1,3}\$?\d+)
  | (?P<func>[A-Z]+(?=\())
  | (?P<op><=|>=|<>|[-+*/^=<>(),:])
""", re.VERBOSE)
FUNCS = {"SUM", "MAX", "MIN", "AVERAGE", "COUNT", "ROUND", "ABS", "IF"}


class FormulaError(ValueError):
    pass


class _Err:
    def __init__(self, msg: str) -> None:
        self.msg = msg


def tokenize(text: str) -> list[tuple[str, str]]:
    out, pos = [], 0
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m:
            raise FormulaError(f"cannot tokenise {text[pos:pos + 20]!r} in {text!r}")
        pos = m.end()
        kind = m.lastgroup
        if kind == "ws":
            continue
        out.append((kind, m.group(kind)))
    return out


class Workbook:
    def __init__(self, path: Path) -> None:
        self.wb = load_workbook(path, data_only=False)
        self.cache: dict[tuple[str, str], object] = {}

    def raw(self, sheet: str, addr: str):
        return self.wb[sheet][addr].value

    def value(self, sheet: str, addr: str):
        key = (sheet, addr.replace("$", ""))
        if key in self.cache:
            return self.cache[key]
        v = self.raw(sheet, key[1])
        if isinstance(v, str) and v.startswith("="):
            v = Parser(self, sheet, tokenize(v[1:])).parse()
        self.cache[key] = v
        return v

    def formulas(self):
        for ws in self.wb.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    if isinstance(c.value, str) and c.value.startswith("="):
                        yield ws.title, c.coordinate, c.value


def _split_ref(ref: str, default_sheet: str) -> tuple[str, str]:
    if "!" in ref:
        sheet, addr = ref.rsplit("!", 1)
        sheet = sheet.strip("'")
    else:
        sheet, addr = default_sheet, ref
    return sheet, addr.replace("$", "")


def _cmp_key(v) -> tuple:
    """Excel ordering for comparisons: numbers < text < logical values; a blank cell compares as 0."""
    if v is None:
        return (0, 0.0)
    if isinstance(v, bool):
        return (2, float(v))
    if isinstance(v, (int, float)):
        return (0, float(v))
    return (1, str(v).lower())


def _num(v) -> float:
    if v is None:
        return 0.0
    if isinstance(v, bool):
        return float(v)
    if isinstance(v, (int, float)):
        return float(v)
    raise FormulaError(f"text {v!r} used in arithmetic")


class Parser:
    def __init__(self, book: Workbook, sheet: str, tokens: list[tuple[str, str]]) -> None:
        self.book, self.sheet, self.toks, self.i = book, sheet, tokens, 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else (None, None)

    def take(self, value: str | None = None):
        tok = self.peek()
        if tok[0] is None or (value is not None and tok[1] != value):
            raise FormulaError(f"expected {value!r}, got {tok!r}")
        self.i += 1
        return tok

    def parse(self):
        v = self.comparison()
        if self.i != len(self.toks):
            raise FormulaError(f"trailing tokens {self.toks[self.i:]}")
        return v

    def comparison(self):
        left = self.additive()
        kind, val = self.peek()
        if kind == "op" and val in ("=", "<>", "<", ">", "<=", ">="):
            self.take()
            right = self.additive()
            a, b = _cmp_key(left), _cmp_key(right)
            return {"=": a == b, "<>": a != b, "<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[val]
        return left

    def additive(self):
        v = self.term()
        while self.peek() in (("op", "+"), ("op", "-")):
            op = self.take()[1]
            r = self.term()
            v = _num(v) + _num(r) if op == "+" else _num(v) - _num(r)
        return v

    def term(self):
        v = self.power()
        while self.peek() in (("op", "*"), ("op", "/")):
            op = self.take()[1]
            r = self.power()
            if op == "*":
                v = _num(v) * _num(r)
            else:
                d = _num(r)
                if d == 0:
                    raise FormulaError("#DIV/0!")
                v = _num(v) / d
        return v

    def power(self):
        v = self.unary()
        while self.peek() == ("op", "^"):
            self.take()
            v = _num(v) ** _num(self.unary())
        return v

    def unary(self):
        if self.peek() == ("op", "-"):
            self.take()
            return -_num(self.unary())
        if self.peek() == ("op", "+"):
            self.take()
            return _num(self.unary())
        return self.primary()

    def _range_values(self, a: str, b: str) -> list:
        sa, aa = _split_ref(a, self.sheet)
        sb, ab = _split_ref(b, self.sheet)
        if sa != sb:
            raise FormulaError("range across sheets")
        ca, ra = re.match(r"([A-Z]+)(\d+)", aa).groups()
        cb, rb = re.match(r"([A-Z]+)(\d+)", ab).groups()
        out = []
        for col in range(column_index_from_string(ca), column_index_from_string(cb) + 1):
            for row in range(int(ra), int(rb) + 1):
                out.append(self.book.value(sa, f"{get_column_letter(col)}{row}"))
        return out

    def argument(self) -> list:
        kind, val = self.peek()
        if kind == "ref":
            nxt = self.toks[self.i + 1] if self.i + 1 < len(self.toks) else (None, None)
            if nxt == ("op", ":"):
                self.take()
                self.take(":")
                end = self.take()
                if end[0] != "ref":
                    raise FormulaError("bad range")
                return self._range_values(val, end[1])
        return [self.comparison()]

    def primary(self):
        kind, val = self.peek()
        if kind == "num":
            self.take()
            return float(val)
        if kind == "str":
            self.take()
            return val[1:-1].replace('""', '"')
        if kind == "ref":
            self.take()
            sheet, addr = _split_ref(val, self.sheet)
            return self.book.value(sheet, addr)
        if kind == "op" and val == "(":
            self.take()
            v = self.comparison()
            self.take(")")
            return v
        if kind == "func":
            name = val
            if name not in FUNCS:
                raise FormulaError(f"unsupported function {name}")
            self.take()
            self.take("(")
            args: list[list] = []

            def one():
                if name != "IF":
                    return self.argument()
                start = self.i
                try:                      # IF is lazy in Excel: keep errors of the branch not taken
                    return self.argument()
                except FormulaError as exc:
                    depth, self.i = 0, start
                    while self.i < len(self.toks):
                        k, v = self.toks[self.i]
                        if v == "(":
                            depth += 1
                        elif v == ")":
                            if depth == 0:
                                break
                            depth -= 1
                        elif v == "," and depth == 0:
                            break
                        self.i += 1
                    return [_Err(str(exc))]
            if self.peek() != ("op", ")"):
                args.append(one())
                while self.peek() == ("op", ","):
                    self.take()
                    args.append(one())
            self.take(")")
            out = self.call(name, args)
            if isinstance(out, _Err):
                raise FormulaError(out.msg)
            return out
        raise FormulaError(f"unexpected token {kind} {val!r}")

    def call(self, name: str, args: list[list]):
        flat = [v for a in args for v in a]
        nums = [float(v) for v in flat if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if name == "SUM":
            return float(sum(nums))
        if name == "MAX":
            return max(nums) if nums else 0.0
        if name == "MIN":
            return min(nums) if nums else 0.0
        if name == "COUNT":
            return float(len(nums))
        if name == "AVERAGE":
            if not nums:
                raise FormulaError("#DIV/0!")
            return sum(nums) / len(nums)
        if name == "ABS":
            return abs(_num(args[0][0]))
        if name == "ROUND":
            return round(_num(args[0][0]), int(_num(args[1][0])))
        if name == "IF":
            cond = args[0][0]
            if isinstance(cond, _Err):
                return cond
            truthy = bool(cond) if not isinstance(cond, str) else cond != ""
            return args[1][0] if truthy else (args[2][0] if len(args) > 2 else False)
        raise FormulaError(name)
