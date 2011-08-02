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

import il, cf

def engine(analyzer, functions):

    def flow_function(A, node, *kids):
        print node
        print kids
        def if_then(x):
            _if = kids[0]
            _then = kids[1]
            r_if = _if(x)
            return A.join(_then(r_if), r_if)

        def if_then_else(x):
            _if = kids[0]
            _then = kids[1]
            _else = kids[2]
            r_if = _if(x)
            return A.join(_then(r_if), _else(r_if))

        def chain(x):
            acc = x
            for c in kids:
                acc = c(acc)
            return acc

        if node.region_type == cf.cfs.CHAIN:
            return chain
        elif node.region_type == cf.cfs.IF_THEN:
            return if_then
        elif node.region_type == cf.cfs.IF_THEN_ELSE:
            return if_then_else
        else:
            raise Exception, "unexpect region type"

    def process_tree(analyzer, f):

        def visit(n):

            if isinstance(n, il.Block):
                return analyzer.flow_function(n)

            kids_ff = [visit(c) for c in n.children]
            return flow_function(analyzer, n, *kids_ff)

        return visit(f.tree)


    f = functions['f2']
    a = analyzer()
    a.init(f)
    ff = process_tree(a, f)
    print ff(set())

    #for f in functions:
        #a = analyzer()
        #a.init(f)
        #process_tree(a, f)
