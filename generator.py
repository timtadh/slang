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
        inn = dict()
        out = list()
        for c in node.children:
            if c.label == 'Takes':
                for d in c.children:
                    name = d.children[0].label
                    typ_ = Type(d.children[1])
                    inn[name] = typ_
            elif c.label == 'Returns':
                for d in c.children:
                    typ_ = Type(d)
                    out.append(typ_)
        return inn, out
    def Type(node):
        if node.label == 'IntType':
            return il.Int()
        elif node.label == 'FuncType':
            inn = list()
            out = list()
            for c in node.children:
                if c.label == 'Params':
                    for t in c.children[0].children:
                        inn.append(Type(t))
                elif c.label == 'Returns':
                    for t in c.children[0].children:
                        out.append(Type(t))
            return il.Func(inn, out)
    def Func(node, objs, inn, out):
        objs = dict(objs)
        objs.update(inn)
        print
        print
        #TODO: parameter logic
        block = Block(node.children[-2], objs)
        #TODO: Return logic / Continue logic
        print inn, out
        print 'Func', objs.keys()
        return block
    def Assign(node, objs):
        #print node
        #print
        if node.children[1].label == 'Call':
            code = Call(
                node.children[1],
                objs,
                [n.label for n in node.children[0].children]
            )
        elif node.children[1].label == 'Func':
            func = node.children[1]
            name = node.children[0].label
            label = 'func_%d' % generate.fcount; generate.fcount += 1
            inn, out = Params(func, objs)
            print name, label, inn, out
            objs[name] = il.Func(inn, out, label=label)
            functions[label] = {
                'code' : Func(func, dict(objs), inn, out),
                'symbols' : objs
            }
            code = 'Todo Func code in assign'
        else:
            raise Exception, 'Unexpected node %s' % (node.children[1].label)
        print 'Assign', objs.keys()
        return code
    def Call(node, objs, returns):
        print 'call returns ->', returns
        print 'Call', objs.keys()
    def Block(node, objs):
        codelist = list()
        for c in node.children:
            if c.label == 'Assign':
                code = Assign(c, objs)
            elif c.label == 'Call':
                code = Call(c, objs, list())
            else:
                raise Exception, 'Unexpected node %s' % (c.label)
        print 'Block', objs.keys()
        return code
    objs = dict(prebuilt_funcs)
    r = Block(root, objs)
    print '---'
    for x,y in functions.iteritems():
        print x
        print ' '*4, 'symbols'
        for a,b in y['symbols'].iteritems():
            print ' '*8, a, b
        print ' '*4, 'code', y['code']
    print '---'
    for x,y in objs.iteritems():
        print x, y
    print '---'
    return r

if __name__ == '__main__':

    root = Parser().parse('''
        end = func(r1 int, r2 int) {
            print(r1)
            print(r2)
            exit()
            return
        }
        add = func(d int, e int)(int) {
            x = __add(d, e)
            return x
        }
        f = func(plus func(int, int)(int), ret func(int, int)) {
            c = plus(2,3)
            continue ret(c, b)
        }
        f(add, end)
    ''', lexer=Lexer())
    print generate(root)
