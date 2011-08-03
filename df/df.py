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

import il, cf, abstract

class results(object):
    def __init__(self):
        self.inn = dict()
        self.out = dict()

def forward(analyzer, functions, debug=False):

    assert issubclass(analyzer, abstract.DataFlowAnalyzer)
    assert analyzer.direction == 'forward'

    def compute(f):

        A = analyzer(f)
        R = results()

        def save(inn, out, node):
            if isinstance(node, il.Block):
                R.inn[node.name] = inn
                R.out[node.name] = out

        def flow_function(node, *kids):

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
                for c, node in kids:
                    newacc = c(acc)
                    save(acc, newacc, node)
                    acc = newacc
                return acc


            if node.region_type == cf.cfs.CHAIN:
                return chain
            elif node.region_type == cf.cfs.IF_THEN:
                return if_then
            elif node.region_type == cf.cfs.IF_THEN_ELSE:
                return if_then_else
            else:
                raise Exception, "unexpect region type"

        def process_tree(f):

            def visit(n):

                if isinstance(n, il.Block):
                    return A.flow_function(n)

                kids_ff = [(visit(c), c) for c in n.children]
                return flow_function(n, *kids_ff)

            if isinstance(f.tree, il.Block):
                blk = f.tree
                ff = A.flow_function(blk)
                def single_block(inn):
                    out = ff(inn)
                    save(inn, out, blk)
                    return out
                return single_block
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



    #compute(functions['f2'])

    for f in functions.itervalues():
        compute(f)
