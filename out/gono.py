import sys
argv = sys.argv
argc = len(argv)


def __snake_format(string, *args, **kwargs):
    return string.format(*args, **kwargs)


def __snake_string_add(string, value):
    return string + value


def __snake_string_remove(string, value):
    return string.replace(value, '')


def __snake_cast(value, target_type):
    if target_type == int:
        return int(value)
    elif target_type == float:
        return float(value)
    elif target_type == str:
        return str(value)
    elif target_type == bool:
        return bool(value)
    else:
        return target_type(value)


def __snake_cast_dict_to_struct(struct_type, dict_value):
    instance = struct_type.__new__(struct_type)
    for key, value in dict_value.items():
        setattr(instance, key, value)
    return instance


class All:
    pass


import random
import functools


class __SnakeMaybeType:

    def __bool__(self):
        return random.choice([True, False])

    @property
    def value(self):
        return random.choice([True, False])

    def __repr__(self) ->str:
        return 'Maybe'


@functools.total_ordering
class __SnakeHalfType:
    value = 0.5

    def __bool__(self):
        return True

    def __repr__(self) ->str:
        return 'Half'

    def __eq__(self, other):
        try:
            return self.value == float(other)
        except (ValueError, TypeError):
            return NotImplemented

    def __lt__(self, other):
        try:
            return self.value < float(other)
        except (ValueError, TypeError):
            return NotImplemented

    def is_equal(self, other):
        try:
            return float(other) == self.value
        except:
            return False

    def is_less(self, other):
        try:
            return float(other) < self.value
        except:
            return False

    def is_greater(self, other):
        try:
            return float(other) > self.value
        except:
            return False


Maybe = __SnakeMaybeType()
Half = __SnakeHalfType()


class ParserExpectedError(Exception):

    def __init__(self, val: str, line: int, expec: str) ->None:
        self.val = val
        self.line = line
        self.expec = expec

    def __str__(self):
        return (
            f"Expected '{self.expec}', but got '{self.val}'. at line: {self.line}"
            )


class ParserTypeError(Exception):

    def __init__(self, val: str, line: int, type: str) ->None:
        self.val = val
        self.line = line
        self.type = type

    def __str__(self):
        return (
            f"Expected value of type '{self.type}', but got '{self.val}' that is another type. at line: {self.line}"
            )


def tokenize(code: str) ->list[tuple[str, int]]:
    lines: list[str] = code.split('\n')
    tks: list[tuple[str, int]] = []
    for i, line in enumerate(lines):
        tokns: list[str] = line.split()
        i: int = 0
        while i < len(tokns):
            tkn: str = tokns[i]
            i: int = i + 1
            if tkn.startswith('"'):
                if tkn.endswith('"'):
                    tks.append((tkn.replace('\\s', ' '), i))
                else:
                    final: list[str] = [tkn]
                    while not tkn.endswith('"') and i < len(tokns):
                        tkn: str = tokns[i]
                        i: int = i + 1
                        final.append(tkn)
                    tks.append((' '.join(final).replace('\\s', ' '), i))
            else:
                tks.append((tkn, i))
    return tks


from enum import Enum


class NodeType(Enum):
    FUNC = 1
    IMPORT = 2


class CallNode:

    def __init__(self, funcname: str, args: list[str]) ->None:
        self.funcname = funcname
        self.args = args

    def __repr__(self) ->str:
        return f'CallNode(funcname={self.funcname}, args={self.args})'


class OtherNode:

    def __init__(self, value: str, line: int) ->None:
        self.value = value
        self.line = line

    def __repr__(self) ->str:
        return f'OtherNode(value={self.value}, line={self.line})'


class SetNode:

    def __init__(self, vname: str, code: All) ->None:
        self.vname = vname
        self.code = code

    def __repr__(self) ->str:
        return f'SetNode(vname={self.vname}, code={self.code})'


class ReturnNode:

    def __init__(self, returncode: All) ->None:
        self.returncode = returncode

    def __repr__(self) ->str:
        return f'ReturnNode(returncode={self.returncode})'


class BlockNode:

    def __init__(self, code: All) ->None:
        self.code = code

    def __repr__(self) ->str:
        return f'BlockNode(code={self.code})'


class IfNode:

    def __init__(self, cond: BlockNode, code: BlockNode) ->None:
        self.cond = cond
        self.code = code

    def __repr__(self) ->str:
        return f'IfNode(cond={self.cond}, code={self.code})'


class ElseNode:

    def __init__(self, code: BlockNode) ->None:
        self.code = code

    def __repr__(self) ->str:
        return f'ElseNode(code={self.code})'


class FuncNode:

    def __init__(self, name: str, args: list[str], block: BlockNode) ->None:
        self.name = name
        self.args = args
        self.block = block

    def __repr__(self) ->str:
        return (
            f'FuncNode(name={self.name}, args={self.args}, block={self.block})'
            )


class ImportNode:

    def __init__(self, filepath: str) ->None:
        self.filepath = filepath

    def __repr__(self) ->str:
        return f'ImportNode(filepath={self.filepath})'


class ProgramNode:

    def __init__(self, code: list[FuncNode, ImportNode]) ->None:
        self.code = code

    def __repr__(self) ->str:
        return f'ProgramNode(code={self.code})'


def parse(tks: list[tuple[str, int]], is_func: bool=False) ->All:
    i: int = 0
    if not is_func:
        prog: ProgramNode = ProgramNode([])
    else:
        prog: BlockNode = BlockNode([])
    while i < len(tks):
        t: tuple[str, int] = tks[i]
        i: int = i + 1
        if t[0] == 'create':
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            fname: str = t[0]
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            if t[0] != ':':
                raise ParserExpectedError(t[0], t[1], ':')
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            args: list[str] = []
            while i < len(tks) and t[0] != ':':
                args.append(t[0])
                t: tuple[str, int] = tks[i]
                i: int = i + 1
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            if t[0] != '{':
                raise ParserExpectedError(t[0], t[1], '{')
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            fcode: list[tuple[str, int]] = []
            en: int = 1
            while en > 0 and i < len(tks):
                if t[0] == '}':
                    en: int = en - 1
                    if en > 0:
                        fcode.append(t)
                elif t[0] == '{':
                    en: int = en + 1
                    fcode.append(t)
                else:
                    fcode.append(t)
                t: tuple[str, int] = tks[i]
                i: int = i + 1
            i: int = i - 1
            prog.code.append(FuncNode(fname, args, parse(fcode, True)))
        elif t[0] == 'import':
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            if not (t[0].startswith('"') and t[0].endswith('"')):
                raise ParserTypeError(t[0], t[1], 'string')
            prog.code.append(ImportNode(t[0][1:-1]))
        elif t[0] == 'call':
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            name: str = t[0]
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            args: list[str] = []
            while t[0] != '::' and i < len(tks):
                args.append(t[0])
                t: tuple[str, int] = tks[i]
                i: int = i + 1
            prog.code.append(CallNode(name, args))
        elif t[0] == 'return':
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            code: list[tuple[str, int]] = []
            while t[0] != '::' and i < len(tks):
                code.append(t)
                t: tuple[str, int] = tks[i]
                i: int = i + 1
            prog.code.append(ReturnNode(parse(code, True)))
        elif t[0] == 'set':
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            name: str = t[0]
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            if t[0] != '->':
                raise ParserExpectedError(t[0], t[1], '->')
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            code: list[tuple[str, int]] = []
            while t[0] != '::' and i < len(tks):
                code.append(t)
                t: tuple[str, int] = tks[i]
                i: int = i + 1
            prog.code.append(SetNode(name, parse(code, True)))
        elif t[0] == '/*':
            while t[0] != '*/' and i < len(tks):
                t: tuple[str, int] = tks[i]
                i: int = i + 1
        elif t[0] == 'if':
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            cond: list[tuple[str, int]] = []
            while t[0] != '{' and i < len(tks):
                cond.append(t)
                t: tuple[str, int] = tks[i]
                i: int = i + 1
            code: list[tuple[str, int]] = []
            en: int = 1
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            while en > 0 and i < len(tks):
                if t[0] == '{':
                    en: int = en + 1
                    code.append(t)
                elif t[0] == '}':
                    en: int = en - 1
                    if en > 0:
                        code.append(t)
                else:
                    code.append(t)
                t: tuple[str, int] = tks[i]
                i: int = i + 1
            i: int = i - 1
            prog.code.append(IfNode(parse(cond, True), parse(code, True)))
        elif t[0] == 'else':
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            if t[0] != '{':
                raise ParserExpectedError(t[0], t[1], '{')
            t: tuple[str, int] = tks[i]
            i: int = i + 1
            code: list[tuple[str, int]] = []
            en: int = 1
            while en > 0 and i < len(tks):
                if t[0] == '{':
                    en: int = en + 1
                    code.append(t)
                elif t[0] == '}':
                    en: int = en - 1
                    if en > 0:
                        code.append(t)
                else:
                    code.append(t)
                t: tuple[str, int] = tks[i]
                i: int = i + 1
            i: int = i - 1
            prog.code.append(ElseNode(parse(code, True)))
        else:
            prog.code.append(OtherNode(t[0], t[1]))
    return prog


import os
outcode: list[str] = ['section .bss', 'buf:    resb    20', '',
    'section .text', 'global _start', '', 'sysc:', '    mov     rax, rbx',
    '    syscall', '    ret', '', 'printi:',
    '    ; — get number from rbx into rax —', '    mov     rax, rbx',
    '    ; — point rsi at end of buffer —', '    lea     rsi, [buf+20]',
    '    xor     rcx, rcx          ; digit count = 0', '    cmp     rax, 0',
    '    jne     .printi_loop', '    ; special‑case zero',
    '    dec     rsi', "    mov     byte [rsi], '0'", '    inc     rcx',
    '    jmp     .printi_done', '.printi_loop:', '    xor     rdx, rdx',
    '    mov     r10, 10           ; divisor in r10',
    '    div     r10               ; rax/=10, rdx=digit',
    "    add     dl, '0'", '    dec     rsi', '    mov     [rsi], dl',
    '    inc     rcx               ; count this digit',
    '    cmp     rax, 0', '    jne     .printi_loop', '.printi_done:',
    '    ; write(1, rsi, rcx)', '    mov     rbx, 1            ; sys_write',
    '    mov     rdi, 1            ; fd = stdout',
    '    mov     rdx, rcx          ; length', '    call    sysc', '    ret']
strs: list[tuple[str, int]] = []
strco: list[int] = [0]
regargs: list[str] = ['rbx', 'rdi', 'rsi', 'rdx', 'r8']
ifn: list[int] = [0]
eqn: list[int] = [0]


def comp_expr(block: BlockNode, args: dict[str, int]={}, varss: dict[str,
    int]={}) ->int:
    i: int = 0
    nodes: All = block.code
    while i < len(nodes):
        n: All = nodes[i]
        i: int = i + 1
        if isinstance(n, OtherNode):
            if n.value.startswith('"') and n.value.endswith('"'):
                strs.append((n.value, strco[0]))
                strco[0] += 1
                outcode.append('  push str{}'.format(strco[0] - 1))
            elif n.value.isdigit():
                outcode.append('  push {}'.format(n.value))
            elif n.value == '+':
                outcode.append('  pop rax')
                outcode.append('  pop r9')
                outcode.append('  add r9, rax')
                outcode.append('  push r9')
                outcode.append('  xor r9, r9')
            elif n.value == '-':
                outcode.append('  pop rax')
                outcode.append('  pop r9')
                outcode.append('  sub r9, rax')
                outcode.append('  push r9')
                outcode.append('  xor r9, r9')
            elif n.value == '*':
                outcode.append('  pop rax')
                outcode.append('  pop r9')
                outcode.append('  imul r9, rax')
                outcode.append('  push r9')
                outcode.append('  xor r9, r9')
            elif n.value == '/':
                outcode.append('  pop r9')
                outcode.append('  pop rax')
                outcode.append('  push rdx')
                outcode.append('  xor rdx, rdx')
                outcode.append('  div r9')
                outcode.append('  pop rdx')
                outcode.append('  push rax')
                outcode.append('  xor r9, r9')
            elif n.value in args.keys():
                outcode.append('  push {}'.format(regargs[args[n.value]]))
            elif n.value == '=':
                outcode.append('  pop rax')
                outcode.append('  pop r9')
                outcode.append('.eq{}:'.format(eqn[0]))
                outcode.append('  cmp r9, rax')
                outcode.append('  je .eqtrue{}'.format(eqn[0]))
                outcode.append('  jmp .eqfalse{}'.format(eqn[0]))
                outcode.append('.eqtrue{}:'.format(eqn[0]))
                outcode.append('  mov rax, 1')
                outcode.append('  jmp .eqend{}'.format(eqn[0]))
                outcode.append('.eqfalse{}:'.format(eqn[0]))
                outcode.append('  mov rax, 0')
                outcode.append('.eqend{}:'.format(eqn[0]))
                outcode.append('  push rax')
                eqn[0] += 1
            elif n.value == '!=':
                outcode.append('  pop rax')
                outcode.append('  pop r9')
                outcode.append('.eq{}:'.format(eqn[0]))
                outcode.append('  cmp r9, rax')
                outcode.append('  jne .eqtrue{}'.format(eqn[0]))
                outcode.append('  jmp .eqfalse{}'.format(eqn[0]))
                outcode.append('.eqtrue{}:'.format(eqn[0]))
                outcode.append('  mov rax, 1')
                outcode.append('  jmp .eqend{}'.format(eqn[0]))
                outcode.append('.eqfalse{}:'.format(eqn[0]))
                outcode.append('  mov rax, 0')
                outcode.append('.eqend{}:'.format(eqn[0]))
                outcode.append('  push rax')
                eqn[0] += 1
            elif n.value == '>':
                outcode.append('  pop rax')
                outcode.append('  pop r9')
                outcode.append('.eq{}:'.format(eqn[0]))
                outcode.append('  cmp r9, rax')
                outcode.append('  jg .eqtrue{}'.format(eqn[0]))
                outcode.append('  jmp .eqfalse{}'.format(eqn[0]))
                outcode.append('.eqtrue{}:'.format(eqn[0]))
                outcode.append('  mov rax, 1')
                outcode.append('  jmp .eqend{}'.format(eqn[0]))
                outcode.append('.eqfalse{}:'.format(eqn[0]))
                outcode.append('  mov rax, 0')
                outcode.append('.eqend{}:'.format(eqn[0]))
                outcode.append('  push rax')
                eqn[0] += 1
            elif n.value == '<':
                outcode.append('  pop rax')
                outcode.append('  pop r9')
                outcode.append('.eq{}:'.format(eqn[0]))
                outcode.append('  cmp r9, rax')
                outcode.append('  jl .eqtrue{}'.format(eqn[0]))
                outcode.append('  jmp .eqfalse{}'.format(eqn[0]))
                outcode.append('.eqtrue{}:'.format(eqn[0]))
                outcode.append('  mov rax, 1')
                outcode.append('  jmp .eqend{}'.format(eqn[0]))
                outcode.append('.eqfalse{}:'.format(eqn[0]))
                outcode.append('  mov rax, 0')
                outcode.append('.eqend{}:'.format(eqn[0]))
                outcode.append('  push rax')
                eqn[0] += 1
            elif n.value == '>=':
                outcode.append('  pop rax')
                outcode.append('  pop r9')
                outcode.append('.eq{}:'.format(eqn[0]))
                outcode.append('  cmp r9, rax')
                outcode.append('  jge .eqtrue{}'.format(eqn[0]))
                outcode.append('  jmp .eqfalse{}'.format(eqn[0]))
                outcode.append('.eqtrue{}:'.format(eqn[0]))
                outcode.append('  mov rax, 1')
                outcode.append('  jmp .eqend{}'.format(eqn[0]))
                outcode.append('.eqfalse{}:'.format(eqn[0]))
                outcode.append('  mov rax, 0')
                outcode.append('.eqend{}:'.format(eqn[0]))
                outcode.append('  push rax')
                eqn[0] += 1
            elif n.value == '<=':
                outcode.append('  pop rax')
                outcode.append('  pop r9')
                outcode.append('.eq{}:'.format(eqn[0]))
                outcode.append('  cmp r9, rax')
                outcode.append('  jle .eqtrue{}'.format(eqn[0]))
                outcode.append('  jmp .eqfalse{}'.format(eqn[0]))
                outcode.append('.eqtrue{}:'.format(eqn[0]))
                outcode.append('  mov rax, 1')
                outcode.append('  jmp .eqend{}'.format(eqn[0]))
                outcode.append('.eqfalse{}:'.format(eqn[0]))
                outcode.append('  mov rax, 0')
                outcode.append('.eqend{}:'.format(eqn[0]))
                outcode.append('  push rax')
                eqn[0] += 1
            elif n.value in varss.keys():
                outcode.append('  mov rax, [rbp-{}]'.format(varss[n.value]))
                outcode.append('  push rax')
    return 0


def comp_block(block: BlockNode, args: list[str]=[]) ->int:
    i: int = 0
    nodes: All = block.code
    offset: int = 1
    varss: dict[str, int] = {}
    while i < len(nodes):
        n: All = nodes[i]
        i: int = i + 1
        if isinstance(n, CallNode):
            cal: int = len(n.args)
            argss: dict[All, int] = {}
            i2: int = 0
            while i2 < len(args):
                argss[args[i2]] = i2
                i2: int = i2 + 1
            for i2, arg in enumerate(n.args):
                if arg.startswith('"') and arg.endswith('"'):
                    strs.append((arg, strco[0]))
                    strco[0] += 1
                    outcode.append('  mov {}, str{}'.format(regargs[i2], 
                        strco[0] - 1))
                elif arg.isdigit():
                    outcode.append('  mov {}, {}'.format(regargs[i2], arg))
                elif arg in varss.keys():
                    outcode.append('  mov {}, [rbp-{}]'.format(regargs[i2],
                        varss[arg]))
                else:
                    outcode.append('  mov {}, {}'.format(regargs[i2],
                        regargs[argss[arg]]))
            outcode.append('  call {}'.format(n.funcname))
            outcode.append('  push rax')
        elif isinstance(n, ReturnNode):
            argss: dict[All, int] = {}
            i2: int = 0
            while i2 < len(args):
                argss[args[i2]] = i2
                i2: int = i2 + 1
            comp_expr(n.returncode, argss, varss)
            outcode.append('  pop rax')
        elif isinstance(n, SetNode):
            argss: dict[All, int] = {}
            i2: int = 0
            while i2 < len(args):
                argss[args[i2]] = i2
                i2: int = i2 + 1
            comp_expr(n.code, argss, varss)
            outcode.append('  pop rax')
            outcode.append('  mov qword [rbp-{}], rax'.format(offset * 8))
            varss[n.vname] = offset * 8
            offset: int = offset + 1
        elif isinstance(n, IfNode):
            argss: dict[All, int] = {}
            i2: int = 0
            while i2 < len(args):
                argss[args[i2]] = i2
                i2: int = i2 + 1
            comp_expr(n.cond, argss, varss)
            outcode.append('  pop rax')
            outcode.append('.ifcond_check{}:'.format(ifn[0]))
            outcode.append('  cmp rax, 1')
            outcode.append('  je .if{}'.format(ifn[0]))
            outcode.append('  jmp .else{}'.format(ifn[0]))
            outcode.append('.if{}:'.format(ifn[0]))
            comp_block(n.code)
            outcode.append('  jmp .ifend{}'.format(ifn[0]))
            outcode.append('.else{}:'.format(ifn[0]))
            if i < len(nodes):
                if isinstance(nodes[i], ElseNode):
                    n: All = nodes[i]
                    i: int = i + 1
                    comp_block(n.code)
            outcode.append('.ifend{}:'.format(ifn[0]))
            ifn[0] += 1
    return 0


def comp(prog: ProgramNode) ->int:
    i: int = 0
    nodes: All = prog.code
    while i < len(nodes):
        n: All = nodes[i]
        i: int = i + 1
        if isinstance(n, ImportNode):
            code: str = open(n.filepath + '.gn', 'r').read()
            comp(parse(tokenize(code)))
        elif isinstance(n, FuncNode):
            outcode.append('{}:'.format(n.name.replace('main', '_start')))
            outcode.append('  push rbp')
            outcode.append('  mov rbp, rsp')
            outcode.append('  sub rsp, 64')
            comp_block(n.block, n.args)
            outcode.append('  leave')
            outcode.append('  ret')
            outcode.append('')
    return 0


def add_strs() ->None:
    for s in strs:
        outcode.append("  str{}: db '{}'".format(s[1], s[0][1:-1].replace(
            '\\n', "', 10, '")))


class NotEnoughArgs(Exception):

    def __init__(self) ->None:
        pass

    def __str__(self):
        return f'Not enough arguments!\nUsage: {argv[0]} input.gn out'


class IncorrectExtension(Exception):

    def __init__(self, ext: str) ->None:
        self.ext = ext

    def __str__(self):
        return f"""Expected extension '.{self.ext}', got unknown extension.
Usage: {argv[0]} input.gn out"""


def main() ->None:
    if argc < 3:
        raise NotEnoughArgs()
    if not argv[1].endswith('.gn'):
        raise IncorrectExtension('gn')
    code: str = open(argv[1], 'r').read()
    comp(parse(tokenize(code)))
    outcode.append('')
    outcode.append('section .data')
    add_strs()
    final_code: str = '\n'.join(outcode)
    with open(argv[2] + '.s', 'w') as out:
        out.write(final_code)
    os.system('nasm -felf64 {} -o {}'.format(argv[2] + '.s', argv[2] + '.o'))
    os.system('ld {} -o {}'.format(argv[2] + '.o', argv[2]))
    os.system('rm {}'.format(argv[2] + '.o'))


if __name__ == '__main__':
    main()
