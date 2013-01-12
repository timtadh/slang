#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

## This file is based off of the work and writings of Steven S. Muchnick
## Muchnick, S. "Advanced Compiler Design & Implementation" Academic Press. 1997. Pg. 202-215

import sys
import textwrap

import struct as cfs
import il

def getnext(n):
    if isinstance(n, il.Block):
        return [b.target for b in n.next]
    else:
        return n.next

def getprev(n):
    if isinstance(n, il.Block):
        return [b.target for b in n.prev]
    else:
        return n.prev

def reaches(s, t):
    visited = set()
    def visit(n):
        if n.name == t.name:
            return True
        visited.add(n.name)
        found = False
        for b in getnext(n):
            if b.name not in visited:
                found = found or visit(b)
            if found:
                break
        return found
    return visit(s)

class analyze(object):
    '''Produce a structural control flow tree for each function. Takes the output of il_gen as
    input.'''

    @classmethod
    def __mock__(cls):
        self = super(analyze, cls).__new__(cls)
        self.__init__()
        self.debug = True
        return self

    def __new__(cls, table, blocks, functions, stdout=None, debug=False):
        #sys.stderr.write('WARNING : Cf broken doing nothing\n')
        #return None
        self = super(analyze, cls).__new__(cls)
        self.debug = debug
        self.__init__()
        if stdout is None: self.stdout = sys.stdout
        self.functions = functions

        ## the control flow analysis modifies the graph as we go.
        ## this is undesirable. we would like the underlying graph
        ## to remain. Therefore, we "push" a copy of the current
        ## graph down and pop it back at the end.
        for blk in blocks.itervalues():
            blk.push_links()

        for f in self.functions.itervalues():
            f.tree = self.structure(f)

        for blk in blocks.itervalues():
            blk.pop_links()

        return None

    def __init__(self):
        pass

    ## A post-order Depth First Search traversal.
    def postorder(self, f):
        '''Produces a post order depth-first-search traversal of the graph of the function f.'''
        visited = set()
        order = list()

        def visit(blk):
            visited.add(blk.name)
            for b in blk.next:
                if b.target.name not in visited:
                    visit(b.target)
            order.append(blk)

        visit(f.entry)
        return order

    def structure(self, f):
        '''Produces a control tree of the function f using structural analysis.'''
        blks = self.postorder(f)

        #postmax = len(blks)-1
        postctr = 0
        while len(blks) > 1 and postctr < len(blks):
            cblk = blks[postctr]

            if self.debug:
                print
                print '-'*80
                print cblk, postctr
                print ' '*8, '\n'.join(
                    textwrap.TextWrapper(
                        width=75, subsequent_indent=' '*8, break_long_words=False,
                    ).wrap(str(blks)))

            ok, rtype, nset = self.acyclic(blks, cblk)
            if ok:
                ## Then we have an acyclic region. reduce the graph.
                newnode, blks, postctr = self.reduce(blks, rtype, nset, postctr)
                #print 'acyclic', postctr
                #if f.entry in nset:
                    #f.entry = newnode
            else:
                ## if nessesary insert cyclic region detection here
                ## right now, I only have if-statements and functions
                ## so there are no inter-block cycles.
                reach_under = set()
                reach_under.add(cblk)
                for blk in blks:
                    if reaches(cblk, blk) and reaches(blk, cblk):
                        reach_under.add(blk)
                print 'reach_under', reach_under
                ok, rtype, nset = self.cyclic(reach_under, cblk)
                if ok:
                    ### Then we have an acyclic region. reduce the graph.
                    newnode, blks, postctr = self.reduce(blks, rtype, nset, postctr)
                    pass
                else:
                    #print 'not acyclic'
                    postctr += 1

            if self.debug:
                print
                print ' '*8, '\n'.join(
                    textwrap.TextWrapper(
                        width=75, subsequent_indent=' '*8, break_long_words=False,
                    ).wrap(str(blks)))
                print '-'*80

        if len(blks) != 1:
            raise Exception, 'Construction of control tree failed'

        return blks[0]

    def reduce(self, blks, rtype, nset, postctr):
        '''Reduces the graph (blks) by replacing the set (nset) with an abstract node of rtype.
        Also updates postctr appropriately.'''

        def compact(blks, node, nset):
            ## TODO: Refactor this method to use one loop
            max_pos = 0
            for i, b in enumerate(blks):
                if b in nset: max_pos = i

            blks[max_pos] = node
            blks = [b for b in blks if b not in nset]
            return blks

        def replace(blks, node, nset, postctr):
            ## TODO: refactor this method to have compact set postctr
            blks = compact(blks, node, nset)
            for i, b in enumerate(blks):
                if b is node: postctr = i; break

            for n in nset:
                for v in getnext(n):
                    if v not in nset:
                        if v not in node.next: node.next.append(v)
                        branch = v.prev.pop(v.prev.index(n))
                        if node not in v.prev:
                            if isinstance(branch, il.Branch):
                                v.prev.append(il.Branch(branch.type, node))
                            else:
                                v.prev.append(node)
                for u in getprev(n):
                    if u not in nset:
                        if u not in node.prev: node.prev.append(u)
                        print n, u.next
                        branch = u.next.pop(u.next.index(n))
                        if node not in u.next:
                            if isinstance(branch, il.Branch):
                                u.next.append(il.Branch(branch.type, node))
                            else:
                                u.next.append(node)
            return blks, postctr

        node = cfs.Node(rtype, nset)
        blks, postctr = replace(blks, node, nset, postctr)
        return node, blks, postctr

    def find_proper(self, n, blks):
        def getnext(n):
            if isinstance(n, il.Block):
                return [b.target for b in n.next if b.type != il.BACKEDGE]
            else:
                return n.next
        visited = set()
        completed = set()
        depth = dict()
        def visit(c, parents):
            visited.add(c.name)
            for kid in getnext(c):
                if kid.name in visited and kid.name not in completed:
                    raise RuntimeError, 'Cyclic structure'
                d = depth.get(kid.name, 0)
                if parents + 1 > d: depth[kid.name] = parents + 1
                if kid.name not in visited:
                    visit(kid, parents + 1)
            completed.add(c.name)
        depth.update({n.name:0})
        visit(n, 0)
        final_name = max(depth, key=lambda x: depth[x])
        visited.remove(final_name)
        return list(blk for blk in blks[::-1] if blk.name in visited)

    ## Adapted from figure 7.41 on page 208
    def acyclic(self, blks, cblk):
        ''' Detects acyclic control flow regions suchs as: chains and if-statements.'''

        nset = set()

        ## BEGIN CHAIN CHECK:
        ##   Check for a chain of blks starting with the current blk
        n = cblk
        p = True                # len(n.prev) == 1 [assume for start of loop]
        s = (len(n.next) == 1)  # len(n.next) == 1 eg. |successor| == 1

        ## look for a chain starting with the current block
        while p and s:
            nset.add(n)
            n = getnext(n)[0]
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
            n = getprev(n)[0]
            p = (len(n.prev) == 1)
            s = (len(n.next) == 1)

        ## the current blk is part of the chain as well.
        if s:
            nset.add(n)

        ## END CHAIN CHECK
        if len(nset) > 1:  # chain
            if self.debug:
                print ' '*12, 'Found Chain'
            return True, cfs.CHAIN, list(blk for blk in blks[::-1] if blk in nset)
        elif len(cblk.next) == 2: # if-then, if-then-else, ...
            if self.debug:
                print ' '*12, 'Found ITE'
                print ' '*12, cblk, cblk.next

            q = r = None
            if isinstance(cblk, il.Block):
                for branch in cblk.next:
                    if branch.type == il.TRUE:
                        assert r is None
                        r = branch.target
                    elif branch.type == il.FALSE:
                        assert q is None
                        q = branch.target
                    else:
                        raise RuntimeError, "Unexpected branch type"
            else:
                r = cblk.next[0]
                q = cblk.next[1]

            print cblk, r, q
            r_next = getnext(r)
            q_next = getnext(q)

            if len(r_next) == 1 and r_next[0] == q: # this is an IF-THEN
                return True, cfs.IF_THEN, [cblk, r]
            elif len(q_next) == 1 and q_next[0] == r: # this is an IF-THEN
                return True, cfs.IF_THEN, [cblk, q]
            elif len(r.prev) == 1 and len(q.prev) == 1:
                if r_next == q_next and len(r_next[0].prev) == 2: # this is an IF-THEN-ELSE
                    return True, cfs.IF_THEN_ELSE, [cblk, r, q]
                else:
                    if self.debug:
                        print ' '*12, 'wat'
                        print ' '*12, r, r.next
                        print ' '*12, q, q.next
            else:
                ## could be an AND or OR or ERROR
                ##kids = sorted([(r, r_index), (q, q_index)], key=lambda x: x[1])
                print blks
                if len(cblk.prev) == 0:
                    return True, cfs.GENERAL_ACYCLIC, self.find_proper(cblk, blks)
                elif len(cblk.prev) == 1 and \
                  any(b.type == il.BACKEDGE for cb in cblk.prev for b in cb.target.prev):
                    return True, cfs.GENERAL_ACYCLIC, self.find_proper(cblk, blks)
                if self.debug:
                    print ' '*12, 'Except Not'
                    print ' '*12, r, r.next
                    print ' '*12, q, q.next

        return False, None, None

    ## Adapted from figure 7.42 on page 208
    def cyclic(self, blks, cblk):
        ''' Detects cyclic control flow regions suchs as while-loops.'''
        for blk in blks:
            if not reaches(cblk, blk):
                raise RuntimeError, 'Improper Region'
        blks.remove(cblk)
        if len(blks) == 1:
            oblk = blks.pop()
            c_next = getnext(cblk)
            o_next = getnext(oblk)
            if len(c_next) == 2 and len(o_next) == 1 and \
               len(cblk.prev) == 2 and len(oblk.prev) ==1:
                return True, cfs.WHILE, [cblk, oblk]

        return False, None, None

