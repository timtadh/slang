#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from sl_parser import Parser, Lexer
import machine as il

prebuilt_funcs = dict()

def generate(root):
    def gen(node, objs):
        print objs
        print node.label
        if node.label == 'Block':
            funcs = dict()
            names = dict()
            code = list()
            for c in node.children:
                if c.label == 'Assign':
                    if c.children[1].label == 'Call':
                        name, _code = gen(c, objs)
                        names[name] =
                    elif c.children[1].label == 'Func':
                        name, _code = gen(c, objs)
                        funcs[name] = _code
                    else:
                        raise Exception, 'Unexpected Node %s' % (c.children[1].label)
                else:
                    code += gen(c, objs)
            return funcs, code
        elif node.label == 'Assign':
            return node.children[0].children[0].label, gen(node.children[1], objs)
        #results = [gen(c, dict(objs)) for c in node.children]
        return list()
    objs = dict(prebuilt_funcs)
    return gen(root, objs)

if __name__ == '__main__':
    root = Parser().parse('''
        f = func(a, b) {
            c = add(a,b)
            return c
        }
        r = f(2,3)
        print(r)
        exit()
    ''', lexer=Lexer())
    func, code = generate(root)
    print func
    print code
