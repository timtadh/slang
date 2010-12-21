#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from sl_parser import Parser, Lexer
import machine as il

prebuilt_funcs = dict()

def generate(root):
    functions = dict()
    generate.fcount = 0
    def Func(node, objs):
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
            name = node.children[0].children[0].label
            label = 'func_%d' % generate.fcount
            objs[name] = {
                'type':'function', 'slot':None,
                'label':label
            }
            generate.fcount += 1
            functions[label] = Func(node.children[1], dict(objs))
            code = [
                (il.IMM, 3, label),
                #TODO: put the value into the slot
            ]
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
        quit = func() {
            exit()
            return
        }
        f = func(a, b) {
            c = add(a,b)
            return c, b
        }
        r, r2 = f(2,3)
        print(r)
        quit()
    ''', lexer=Lexer())
    print generate(root)