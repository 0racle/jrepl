#!/usr/bin/env python3

import os
import re

from ctypes import CDLL, c_void_p, c_char_p

from pygments import lex
from pygments.lexers import load_lexer_from_file
from pygments.styles import get_style_by_name
from pygments.console import colorize

from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer

from prompt_toolkit.styles.pygments import style_from_pygments_cls

from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import print_formatted_text as fprint

from prompt_toolkit.styles import Style

from prompt_toolkit.history import InMemoryHistory

from pathlib import Path

jellybeans = Style.from_dict(
    {
        "pygments.name": "fg:#ffd787",  # noun
        "pygments.name.tag": "fg:#ffaf5f",  # rank
        "pygments.name.label": "fg:#5f8787",  # control
        "pygments.name.function": "fg:#5fd7ff",  # header
        "pygments.name.decorator": "fg:#5fd7ff",  # def
        "pygments.comment.hashbang": "fg:#87afd7",  # hashbang
        "pygments.comment": "fg:#808080",  # comment
        "pygments.operator": "fg:#8787af",  # verb
        "pygments.keyword": "fg:#d7afff",  # conjunction
        "pygments.keyword.type": "fg:#ffaf5f",  # adverb
        "pygments.literal.string": "fg:#87af5f",  # string
        "pygments.punctuation": "fg:#adadad",
        "pygments.punctuation.marker": "fg:#87afd7",  # parens
        "pygments.literal.number": "fg:#d75f5f",  # number
    }
)

J_BIN = "/opt/j9.5/bin"
J_LIB = f"{J_BIN}/libj.so"
J_PRO = f"{J_BIN}/profile.ijs"


class J:
    def __init__(self, load_profile=False):
        self.libj = CDLL(J_LIB)
        self.libj.JInit.restype = c_void_p
        self.libj.JGetR.restype = c_char_p
        self.jt = c_void_p(self.libj.JInit())
        if load_profile:
            self.do(f"0!:0<'{J_PRO}'[BINPATH_z_=:'{J_BIN}'[ARGV_z_=:''")

    def do(self, expr):
        return self.libj.JDo(self.jt, expr.encode())

    def getr(self):
        return self.libj.JGetR(self.jt).decode(errors="ignore")

    def eval(self, expr):
        self.do(expr)
        return self.getr()


j = J(load_profile=True)

CURPATH = Path(__file__).parent
localpath = lambda fname: CURPATH.joinpath(fname)

repr_ijs = localpath("repr.ijs")
j.eval(f"load '{repr_ijs}'")


def put(string):
    print(string, end="")


convert = lambda x: x.replace(r'\040', ' ').replace(r'\134', '\\')
histfile = os.getenv("HOME") + "/.jhistory"
with open(histfile) as fd:
    _, *lines = map(convert, fd.read().splitlines())
hist = InMemoryHistory(lines)

session = PromptSession(history=hist)

JLexer = load_lexer_from_file(localpath("jlexer.py")).__class__
jlex = PygmentsLexer(JLexer)

style_name = "one-dark"
style = style_from_pygments_cls(get_style_by_name(style_name))
style = jellybeans

opts = {
    "hr": True,
    "repr": True,
    "colout": True,
}
re_opts = re.compile(f"\)({'|'.join(opts.keys())})\s+(on|off)")


def hr():
    if not opts["hr"]:
        return ""
    line = j.eval("({. wcsize_j_ '') # 7 u: '╍'")
    if opts["colout"]:
        line = colorize("cyan", line)
    return line


put(colorize("yellow", j.eval("JVERSION")))
put(hr())

vals = {"on": True, "off": False}


def setopt(key, val):
    old = ["off", "on"][opts[key]]
    opts[key] = vals[val]
    msg = f"Setting '{key}' to {val} (was {old})"
    print(colorize("yellow", msg))


last_repl_ = "last_repl_\s*=.\s*"
last_repl_re = re.compile(last_repl_)


def format_error(out):
    msg = []
    dedent = False
    for line in out.splitlines():
        if last_repl_re.search(line):
            line = re.sub(last_repl_, "", line)
            dedent = True
        elif dedent:
            m = re.search("(^\|\s+)\^\s*$", line)
            if m:
                s = " " * (len(m.groups()[0]) - len(last_repl_))
                line = re.sub("^\|\s+", s, line)
        msg.append(line)
    return "\n".join(msg)


j.eval("(9!:37) 0 _ 0 _")

while True:
    try:
        expr = session.prompt("   ", lexer=jlex, style=style, enable_suspend=True)
    except (KeyboardInterrupt, EOFError):
        with open(histfile, "w") as fd:
            cmap = {ord(' '): r'\040',  ord('\\'): r'\134'}
            print("_HiStOrY_V2_", file=fd)
            for line in hist.get_strings():
                print(line.translate(cmap), file=fd)

        exit()

    if re_opts.match(expr):
        try:
            key, val = expr[1:].split()
            setopt(key, val)
            if opts["hr"]:
                put(hr())
            continue
        except:
            pass

    if len(expr.strip()) == 0:
        continue

    try:
        out = ""
        if opts["repr"]:
            ret = j.do(f"last_repl_ =. {expr}")
            res = j.getr().strip()
            if ret == 0:
                if len(res) > 0:  # eg. 'echo'
                    print(res)
                out = j.eval("Repr < 'last_repl_'")
                j.do("last_repl_ =. (0$0)")
            else:
                out = j.getr()
                msg = format_error(out)
                print(colorize("yellow", msg))
                hr()
                continue
        else:
            out = j.eval(expr)
    except KeyboardInterrupt:
        print("SIGINT")
        continue

    if len(out) == 0:
        continue
    if opts["colout"]:
        tokens = lex(out, lexer=JLexer())
        fprint(PygmentsTokens(tokens), style=style, end="")
    else:
        put(out)
    put(hr())
