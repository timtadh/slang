#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

#------------------------------------------------------------------------#
#                                                                        #
#                     Dataflow Analysis Procedure                        #
#                                                                        #
# Steps:                                                                 #
# 1. For each block b                                                    #
#        compute transform function. This dependence on the analysis     #
#        to be computed. eg. The transform will be different for         #
#        live variable than for reaching definition. Thus requiring      #
#        a "plugin" architecture.                                        #
#                                                                        #
#        let the flow function becalled Fb                               #
#                                                                        #
# 2. Using the `Control Tree Representation` of each procedure compute   #
#    the intra-procedural dataflow information.                          #
#                                                                        #
#    The algorithms is two pass over the nodes of the control-tree.      #
#                                                                        #
#    The first pass is a bottom-up over the nodes in the tree. It        #
#    computes the flow functions for each node. The basic blocks should  #
#    have already been computed in step one and the internal nodes       #
#    should be schematically constructed.                                #
#                                                                        #
#    The second pass is top-down. It starts from the node representing   #
#    the entire procedure and from the initial node (entry for forward   #
#    problems, exit for backward). It then evaluates the date-flow       #
#    functions that propagate the flow information through out the tree. #
#                                                                        #
#    The meet and join operators like the flow functions themselves      #
#    depend on the particular problem being solved. So in general        #
#    they will also need to be inputs into the procedure                 #
#                                                                        #
#------------------------------------------------------------------------#


#------------------------------------------------------------------------#
# Other Thoughts
#
# 1. The Kleene Star and other operators also are dependent on the
#    underlying latice
#
#------------------------------------------------------------------------#

import functools

import il, cf, abstract

class results(object):

    def __init__(self):
        self.inn = dict()
        self.out = dict()

    def save(self, inn, out, node):

        if isinstance(node, il.Block):
            self.inn[node.name] = inn
            self.out[node.name] = out

def analyze(analyzer, functions, debug=False, attach_method=False):

    assert issubclass(analyzer, abstract.DataFlowAnalyzer)
    assert (not attach_method) or hasattr('get_result_method', analyzer)

    def compute(f):

        A = analyzer(f)
        R = results()

        if A.direction == 'forward':
            flow_function = functools.partial(forward_ff, A, R.save)
        elif A.direction == 'backward':
            flow_function = functools.partial(backward_ff, A, R.save)
        else:
            raise Exception, "Unexpected analysis direction."


        def process_tree(f):

            def visit(n):
                if isinstance(n, il.Block):
                    return A.flow_function(n)

                kids_ff = [(visit(c), c) for c in n.children]
                return flow_function(n, *kids_ff)

            if isinstance(f.tree, il.Block):
                blk = f.tree
                return flow_function(blk)
            else:
                return visit(f.tree)

        ff = process_tree(f)
        ff(A.newelement())
        f.df[A.name] = R

        if debug:
            print f.name
            for blk in f.blks:
                print ' '*2, blk
                print ' '*4, 'in ', R.inn[blk.name]
                print ' '*4, 'out', R.out[blk.name]
                print

    for f in functions.itervalues():
        compute(f)
        if attach_method:
            name, m = analyzer.get_result_method()
            setattr(f, name, types.MethodType(m, il.Function, f))

def forward_ff(A, save, node, *kids):

    def if_then(x):
        _if, node_if = kids[0]
        _then, node_then = kids[1]
        r_if = _if(x)
        r_then = _then(r_if)
        result = A.join(r_then, r_if)
        save(x, r_if, node_if)
        save(r_if, r_then, node_then)
        return result

    def if_then_else(x):
        _if, node_if = kids[0]
        _then, node_then = kids[1]
        _else, node_else = kids[2]
        r_if = _if(x)
        r_then = _then(r_if)
        r_else = _else(r_if)
        result =  A.join(r_then, r_else)
        save(x, r_if, node_if)
        save(r_if, r_then, node_then)
        save(r_if, r_else, node_else)
        return result

    def chain(x):
        acc = x
        for f, node in kids:
            newacc = f(acc)
            save(acc, newacc, node)
            acc = newacc
        return acc

    def single_block(inn):
        out = A.flow_function(node)(inn)
        save(inn, out, node)
        return out

    if isinstance(node, il.Block):
        return single_block
    elif node.region_type == cf.cfs.CHAIN:
        return chain
    elif node.region_type == cf.cfs.IF_THEN:
        return if_then
    elif node.region_type == cf.cfs.IF_THEN_ELSE:
        return if_then_else
    else:
        raise Exception, "unexpect region type"

def backward_ff(A, save, node, *kids):

    def if_then(out_it):
        print 'flow function for if_then', [node for f, node in kids]
        _if, node_if = kids[0]
        _then, node_then = kids[1]
        in_then = _then(out_it)
        out_if = A.join(in_then, out_it)
        in_it = in_if = _if(out_if)
        save(in_then, out_it, node_then)
        save(in_if, out_if, node_if)
        return in_it

    def if_then_else(out_ite):
        print 'flow function for if_then_else', [node for f, node in kids]
        _if, node_if = kids[0]
        _then, node_then = kids[1]
        _else, node_else = kids[2]
        in_then = _then(out_ite)
        in_else = _else(out_ite)
        out_if = A.join(in_then, in_else)
        in_it = in_if = _if(out_if)
        save(in_then, out_ite, node_then)
        save(in_else, out_ite, node_else)
        save(in_if, out_if, node_if)
        return in_it

    def chain(out_chain):
        print 'flow function for chain', [node for f, node in kids]
        acc = out_chain
        for f, node in kids[-1::-1]:
            newacc = f(acc)
            save(newacc, acc, node)
            acc = newacc
        return acc

    def single_block(out):
        inn = A.flow_function(node)(out)
        save(inn, out, node)
        return inn

    if isinstance(node, il.Block):
        return single_block
    elif node.region_type == cf.cfs.CHAIN:
        return chain
    elif node.region_type == cf.cfs.IF_THEN:
        return if_then
    elif node.region_type == cf.cfs.IF_THEN_ELSE:
        return if_then_else
    else:
        raise Exception, "unexpect region type"

