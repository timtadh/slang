#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

## This file is based off of the work and writings of Steven S. Muchnick
## Muchnick, S. "Advanced Compiler Design & Implementation" Academic Press. 1997. Pg. 202-215

import sys

import cf_struct as cfs

class analyze(object):

    @classmethod
    def __mock__(cls):
        self = super(analyze, cls).__new__(cls)
        self.__init__()
        return self

    def __new__(cls, entry, blocks, functions, stdout=None):
        self = super(analyze, cls).__new__(cls)
        self.__init__()
        if stdout is None: self.stdout = sys.stdout
        self.functions = functions

        for blk in blocks.itervalues():
            blk.push_links()

        for f in self.functions.itervalues():
            print f.name
            f.tree = self.structure(f)
            print
        print

        for blk in blocks.itervalues():
            blk.pop_links()

        for blk in blocks.itervalues():
            print blk
            print 'next', blk.next
            print 'prev', blk.prev

        return None

    def __init__(self):
        pass

    ## A post-order Depth First Search traversal.
    def postorder(self, f):

        visited = set()
        order = list()

        def visit(blk):
            visited.add(blk.name)
            for b in blk.next:
                if b.name not in visited:
                    visit(b)
            order.append(blk)

        visit(f.entry)
        return order

    def structure(self, f):
        blks = self.postorder(f)

        #postmax = len(blks)-1
        postctr = 0
        while len(blks) > 1 and postctr <= len(blks):
            cblk = blks[postctr]
            ok, rtype, nset = self.acyclic(blks, cblk)
            if ok:
                #print ok, cfs.typesr[rtype], nset
                newnode, blks, postctr = self.reduce(blks, rtype, nset, postctr)
                if f.entry in nset:
                    f.entry = newnode
                #raise Exception, "reduce"

            elif False:
                pass
                ## if nessesary insert cyclic region detection here
                ## right now, I only have if-statements and functions
                ## so there are no inter-block cycles.
            else:
                postctr += 1

        if len(blks) != 1:
            raise Exception, 'Construction of control tree failed'

        return blks[0]

    def reduce(self, blks, rtype, nset, postctr):
        node = cfs.Node(rtype, nset)
        blks, postctr = self.replace(blks, node, nset, postctr)
        return node, blks, postctr

    def replace(self, blks, node, nset, postctr):
        blks = self.compact(blks, node, nset)
        for i, b in enumerate(blks):
            if b is node: postctr = i + 1

        for n in nset:
            for v in n.next:
                if v not in nset:
                    node.next.append(v)
                    v.prev.remove(n)
                    v.prev.append(node)
            for u in n.prev:
                if u not in nset:
                    node.prev.append(u)
                    u.next.remove(n)
                    u.next.append(node)

        return blks, postctr

    def compact(self, blks, node, nset):
        max_pos = 0
        for i, b in enumerate(blks):
            if b in nset: max_pos = i

        blks[max_pos] = node
        blks = [b for b in blks if b not in nset]
        return blks

    ## Adapted from figure 7.41 on page 208
    def acyclic(self, blks, cblk):
        nset = oset()

        ## BEGIN CHAIN CHECK:
        ##   Check for a chain of blks starting with the current blk
        n = cblk
        p = True                # len(n.prev) == 1 [assume for start of loop]
        s = (len(n.next) == 1)  # len(n.next) == 1 eg. |successor| == 1

        ## look for a chain starting with the current block
        while p and s:
            nset.add(n)
            n = n.next[0]
            p = (len(n.prev) == 1)
            s = (len(n.next) == 1)

        ## the current blk is part of the chain as well.
        if p:
            nset.add(n)

        ## now look backwards
        n = cblk
        p = (len(n.prev) == 1)
        s = True
        while p and s:
            nset.add(n)
            n = n.prev[0]
            p = (len(n.prev) == 1)
            s = (len(n.next) == 1)

        ## the current blk is part of the chain as well.
        if s:
            nset.add(n)

        ## END CHAIN CHECK
        if len(nset) > 1:  # chain
            return True, cfs.CHAIN, nset
        elif len(cblk.next) == 2: # if-then, if-then-else, ...
            r = cblk.next[0]
            q = cblk.next[1]

            if r.next == q.next and len(r.next[0].prev) == 2: # this is an IF-THEN-ELSE
                return True, cfs.IF_THEN_ELSE, [cblk, r, q, r.next[0]]
            elif r.next[0] == q: # this is an IF-THEN
                return True, cfs.IF_THEN, [cblk, r, q]

        return False, None, None

