#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, collections

import cf
import table

opsr = (
    'MV', 'ADD', 'SUB', 'MUL', 'DIV', 'CALL', 'IPRM', 'OPRM', 'GPRM', 'RPRM',
    'EXIT', 'RTRN', 'CONT', 'IMM', 'PRNT', 'NOP', 'J',
    'IFEQ', 'IFNE', 'IFLT', 'IFLE', 'IFGT', 'IFGE',
    #'IFNEQ', 'IFNNE', 'IFNLT', 'IFNLE', 'IFNGT', 'IFNGE',
    # 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE', 'BEQZ',
)
ops = dict((k, i) for i, k in enumerate(opsr))
sys.modules[__name__].__dict__.update(ops)

branch_typesr = ('UNCONDITIONAL', 'TRUE', 'FALSE')
branch_types = dict((k, i) for i, k in enumerate(branch_typesr))
sys.modules[__name__].__dict__.update(branch_types)

def run(table, blocks, functions, *args, **kwargs):
    return _run(functions['main'].entry.name, blocks, functions, *args, **kwargs)

def _run(entry, blocks, functions, params=None, var=None, stdout=None):
    if stdout == None: stdout = sys.stdout
    if var is None: var = table.SymbolTable()
    nparams = list()
    rparams = list()
    irparams = list()
    il = blocks[entry].insts
    blk = entry
    c = 0
    while c < len(il):
        i = il[c]
        if i.op == IMM:
            var[i.result.name] = i.a
        elif i.op == DIV:
            var[i.result.name] = var[i.a.name] / var[i.b.name]
        elif i.op == MUL:
            var[i.result.name] = var[i.a.name] * var[i.b.name]
        elif i.op == SUB:
            var[i.result.name] = var[i.a.name] - var[i.b.name]
        elif i.op == ADD:
            var[i.result.name] = var[i.a.name] + var[i.b.name]
        elif i.op == MV:
            var[i.result.name] = var[i.a.name]
        elif i.op == PRNT:
            print >>stdout, var[i.a.name]
        elif i.op == IPRM:
            if isinstance(i.b.type, Func):
                nparams.insert(i.a, i.b)
            else:
                nparams.insert(i.a, var[i.b.name])
        elif i.op == OPRM:
            rparams.insert(i.a, var[i.b.name])
        elif i.op == GPRM:
            var[i.result.name] = params[i.a]
        elif i.op == RPRM:
            var[i.result.name] = irparams[i.a]
        elif i.op == CALL:
            var = var.push()
            if isinstance(i.a.type, Func):
                _entry = functions[i.a.type.name].entry.name
                irparams = _run(_entry, blocks, functions, nparams, var, stdout=stdout)
            else:
                _entry = functions[var[i.a.name].type.name].entry.name
                irparams = _run(_entry, blocks, functions, nparams, var, stdout=stdout)
            var = var.pop()
            nparams = list()
        elif i.op == RTRN:
            return rparams
        elif i.op in [IFEQ, IFNE, IFLT, IFLE, IFGT, IFGE]:
            ops = {
                IFEQ : (lambda a,b: var[a.name] == var[b.name]),
                IFNE : (lambda a,b: var[a.name] != var[b.name]),
                IFLT : (lambda a,b: var[a.name] < var[b.name]),
                IFLE : (lambda a,b: var[a.name] <= var[b.name]),
                IFGT : (lambda a,b: var[a.name] > var[b.name]),
                IFGE : (lambda a,b: var[a.name] >= var[b.name]),
            }
            if ops[i.op](i.a, i.b):
                blk = i.result.name
                il = blocks[i.result.name].insts
                c = 0
                continue;
        elif i.op == J:
            blk = i.a.name
            il = blocks[i.a.name].insts
            c = 0
            continue;
        elif i.op == NOP:
            pass
        else:
            raise Exception, opsr[i.op]
        c += 1

class Branch(object):

    __slots__ = ['type', 'target']

    def __init__(self, type, target):
        assert type in branch_types.values()
        self.type = type
        self.target = target

    def __eq__(self, other):
        if isinstance(other, Branch):
            return self.type == other.type and self.target == other.target
        elif isinstance(other, Block):
            return self.target == other
        elif isinstance(other, cf.struct.Node):
            return self.target == other
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self): return str(self)

    def __str__(self):
        return '<Branch %s %s>' % (branch_typesr[self.type], str(self.target))

class Block(object):

    def __init__(self, name):
        self.name = name
        self.insts = list()
        self.next = list()
        self.prev = list()
        self.all_pred = set()
        self.link_stack = list()

    def __eq__(self, other):
        if isinstance(other, Block):
            return self.name == other.name
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def push_links(self):
        self.link_stack.append({'next':self.next, 'prev':self.prev})
        self.next = list(self.next)
        self.prev = list(self.prev)

    def pop_links(self):
        next = self.next
        prev = self.prev
        old = self.link_stack.pop()
        self.next = old['next']
        self.prev = old['prev']
        return next, prev

    def link(self, blk, branch_type):
        if blk in self.next: return
        self.next.append(Branch(branch_type, blk))
        blk.prev.append(self)

    def dotty(self):
        def string(n):
            #if isinstance(s, Node): return str(s.label)
            if isinstance(n, Block):
                s = '      Block %s\n' % (n.name)
                s += '\n'.join("%-4s %-17s %-17s %s" % (opsr[i.op], i.a, i.b, i.result) for i in n.insts)
            else:
                s = str(n)
            s = (
                s.replace("'", "\\'").
                replace('"', '\\"').
                replace('\n', '\\n').
                replace('<', '[').
                replace('>', ']')
            )
            s = ''.join(
              '<tr><td align="left">' + line + "</td></tr>"
              for line in s.split('\\n'))
            return s

        def add_node(nodes, name, label):
            nodes.append(node % locals())
        node = '%(name)s [shape=rect, fontname="Courier", label=<<table border="0">%(label)s</table>>];'
        edge = '%s -> %s [taillabel="%s"];'
        backedge = '%s -> %s:w [taillabel="%s"];'
        nodes = list()
        edges = list()

        i = 0
        queue = collections.deque()
        queue.append((i, self))
        visited = dict()
        i += 1
        while len(queue) > 0:
            c, n = queue.pop()
            if n.name in visited:
                name = visited[n.name]
            else:
                name = 'n%d' % c
                visited[n.name] = name
                add_node(nodes, name, string(n))
            for v in n.next:
                e_template = edge
                if v.target.name in visited:
                    if cf.reaches(v.target, n):
                        e_template = backedge
                    vname = visited[v.target.name]
                else:
                    vname = 'n%d' % i
                    visited[v.target.name] = vname
                    queue.append((i, v.target))
                    add_node(nodes, vname, string(v.target))
                    i += 1
                edge_label = ''
                if v.type != UNCONDITIONAL:
                    edge_label = branch_typesr[v.type][0]
                edges.append(e_template % (name, vname, edge_label))
        return 'digraph G {\nrankdir=LR;\n' + '\n'.join(nodes) + '\n' + '\n'.join(edges) + '\n}\n'

    def __repr__(self): return str(self)

    def __str__(self):
        return '<Block %s>' % self.name

class Function(object):

    def __init__(self, name):
        self.name = name
        self.entry = None            # the entry to the func, a basic block
        self.exit = None             # the exit from the func, a basic block
        self.blks = list()           # the basic blocks in the func as a list
        self.next = list()           # the functions called by this function
        self.params = list()         # the params this function takes
        self.oparam_count = 0        # the number of output parameters
        self.tree = None             # the structure C.F. representation
        self.df = dict()             # dataflow results.
        self.scope_depth = None      # what the scope depth the function was
                                     # declared at

    def __repr__(self): return str(self)

    def __str__(self):
        return '<Function %s %s entry:%s exit:%s params:%s oparams:%i>' % (self.name, str([b for b in self.blks]), str(self.entry), str(self.exit), str(self.params), self.oparam_count)

class Inst(object):

    def __init__(self, op, a, b, result):
        self.op     = op
        self.a      = a
        self.b      = b
        self.result = result

    def __repr__(self): return str(self)

    def __str__(self):
        if not self.result:
            return '%-5s %-18s %-18s' % (opsr[self.op], str(self.a), str(self.b))
        return '%-5s %-18s %-18s --> %s' % (opsr[self.op], str(self.a), str(self.b), str(self.result))

class Symbol(object):

    IDC = 0

    def __init__(self, name, type):
        self._id = Symbol.IDC
        Symbol.IDC += 1
        self.name = name
        self.type = type
        self.scope_depth = None

    def clone(self, b):
        self.name = b.name
        self.type = b.type
        self.scope_depth = b.scope_depth

    def islocal(self, func):
        #print self, self.scope_depth, '?', func.scope_depth
        if self.scope_depth is None: return True
        return func.scope_depth == self.scope_depth

    @property
    def id(self):
        return self._id

    def __repr__(self):
        return '[sym %d - %s%s]' % (self.id, self.name, self.type)

    def __str__(self): return '[sym %s%s]' % (self.name, self.type)

class Type(object):

    IDC = 0

    def __init__(self):
        self._id = Type.IDC
        Type.IDC += 1

    @property
    def id(self):
        return self._id

    def cast(self, cls):
        raise TypeError, "invalid cast"

class Null(Type):

    def __repr__(self):
        return '{Null}'


class Int(Type):

    def __init__(self, basereg=None, offset=None):
        self.basereg = basereg
        self.offset = offset
        super(Int, self).__init__()

    def cast(self, cls):
        if cls is FuncPointer:
            return FuncPointer(self.basereg, self.offset)
        return super(Int, self).cast(cls)

    def __repr__(self):
        if self.basereg is None:
            return '{Int%d}' % (self.id)
        return '{Int%d %s %s}' % (self.id, self.basereg, self.offset)

class Func(Type):

    def __init__(self, name):
        self._entry = name
        super(Func, self).__init__()

    @property
    def name(self):
        return self._name

    @name.setter
    def entry(self, val):
        self._name = val

    def __repr__(self):
        return '{Func%d %s}' % (self.id, str(self.entry))

class FuncPointer(Int):
    def __repr__(self):
        if self.basereg is None:
            return '{FuncPointer%d}' % (self.id)
        return '{FuncPointer%d %s %s}' % (self.id, self.basereg, self.offset)
