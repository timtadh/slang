#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from sl_parser import Parser, Lexer
import il

prebuilt_funcs = dict()

def generate(root):
    functions = dict()
    generate.fcount = 0
    def Params(node, objs):
        inn = 0
        out = 0
        if node.children[0].label == 'Dparams':
            inn = len(node.children[0].children)
        if node.children[-1].label == 'Return':
            out = len(node.children[-1].children)
        return inn, out
    def Func(node, objs):
        if node.children[0].label == 'Dparams':
            pass
        print 'Func', objs.keys()
    def Assign(node, objs):
        if node.children[1].label == 'Call':
            for i, name in \
              enumerate(n.children[0].label
                    for n in node.children[0].children
              ):
                objs[name] = {'type':'value', 'slot':None, 'arg': i}
            code = Call(node.children[1], objs)
        elif node.children[1].label == 'Func':
            func = node.children[1]
            name = node.children[0].children[0].label
            label = 'func_%d' % generate.fcount; generate.fcount += 1
            inn, out = Params(func, objs)
            objs[name] = il.Func(label, inn, out)
            functions[label] = Func(func, dict(objs))
        else:
            raise Exception, 'Unexpected node %s' % (node.children[1].label)
        print 'Assign', objs.keys()
    def Call(node, objs):
        print 'Call', objs.keys()
    def Block(node, objs):
        codelist = list()
        for c in node.children:
            if c.label == 'Assign':
                code = Assign(c, objs)
            elif c.label == 'Call':
                pass
            else:
                raise Exception, 'Unexpected node %s' % (c.label)
        print 'Block', objs.keys()
        return code
    objs = dict(prebuilt_funcs)
    r = Block(root, objs)
    print '---'
    for x,y in objs.iteritems():
        print x, y
    return r

if __name__ == '__main__':

    root = Parser().parse('''
        end = func(r1 int, r2 int) {
            print(r1)
            print(r2)
            exit()
            return
        }
        f = func(a int, b int, end func) {
            c = add(a,b)
            continue end(c, b)
        }
        f(2,3, end)
    ''', lexer=Lexer())
    print generate(root)
