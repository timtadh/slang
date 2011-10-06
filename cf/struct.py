#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, collections

import il

typesr = (
    'CHAIN', 'IF_THEN', 'IF_THEN_ELSE',
)
types = dict((k, i) for i, k in enumerate(typesr))
sys.modules[__name__].__dict__.update(types)

class Node(object):

    def __init__(self, rtype, nset):
        self.region_type = rtype
        self.children = list(nset)
        self.next = list()
        self.prev = list()

    @property
    def name(self):
        return (
            '(%s : %s)'
        ) % (typesr[self.region_type], ' '.join([b.name for b in self.children]))

    def dotty(self):
        def string(n):
            if isinstance(n, Node):
                s = str(typesr[n.region_type])
            elif isinstance(n, il.Block):
                s = '      Block %s\n' % (n.name)
                s += '\n'.join("%-4s %-17s %-17s %s" % (il.opsr[i.op], i.a, i.b, i.result) for i in n.insts)
            else:
                s = str(n)
            return (
                s.replace("'", "\\'").
                replace('"', '\\"').
                replace('\n', '\\n').
                replace('<', '[').
                replace('>', ']')
                #replace('\\', '\\\\')
                )

        node = '%(name)s [shape=rect, label="%(label)s"];'
        leaf = '%(name)s [shape=rect, fontname="Courier", label=<<table border="0">%(label)s</table>>, style="filled", fillcolor="#dddddd"];'
        edge = '%s -> %s;'
        nodes = list()
        edges = list()

        i = 0
        queue = collections.deque()
        queue.append((i, self))
        i += 1
        while len(queue) > 0:
            c, n = queue.popleft()
            name = 'n%d' % c
            label = string(n)
            if not hasattr(n, 'children'):
                #print '--------'
                label = ''.join('<tr><td align="left">' + line + "</td></tr>" for line in label.split('\\n'))
                #print '----------'
                text = leaf % locals()
                nodes.append(text)
            else: nodes.append(node % locals())
            if not hasattr(n, 'children'): continue
            for c in n.children:
                edges.append(edge % (name, ('n%d' % i)))
                queue.append((i, c))
                i += 1
        return 'digraph G {\n' + '\n'.join(nodes) + '\n' + '\n'.join(edges) + '\n}\n'

    def __repr__(self): return str(self)

    def __str__(self):
        return (
            '<cf.Node %s (%s)>'
        ) % (typesr[self.region_type], ' '.join([b.name for b in self.children]))
