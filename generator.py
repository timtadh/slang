#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from sl_parser import Parser, Lexer
from table import SymbolTable
import il

prebuilt_funcs = {
    'print':il.Func([{'type':il.Int(), 'name':None}], []),
    '__add':il.Func(
        [{'type':il.Int(), 'name':None}, {'type':il.Int(), 'name':None}],
        [{'type':il.Int(), 'name':None}]
    ),
    'exit':il.Func([], [])
}

def generate(root):
    functions = dict()
    generate.fcount = 0
    def Params(node, objs):
        inn = list()
        out = list()
        for c in node.children:
            if c.label == 'Takes':
                for d in c.children:
                    name = d.children[0].label
                    typ_ = Type(d.children[1])
                    inn.append({'name':name, 'type':typ_})
            elif c.label == 'Returns':
                for d in c.children:
                    out.append(Type(d))
        print '----->', inn, out
        return inn, out
    def Type(node):
        if node.label == 'IntType':
            return il.Int()
        elif node.label == 'FuncType':
            inn = list()
            out = list()
            for c in node.children:
                if c.label == 'Takes':
                    for t in c.children:
                        inn.append({'name':None, 'type':Type(t)})
                elif c.label == 'Returns':
                    for t in c.children:
                        out.append(Type(t))
            return il.Func(inn, out)
    def Func(node, objs, inn, out):
        for obj in inn:
            objs[obj['name']] = obj['type']
        #print
        #print
        #TODO: parameter logic
        block = Block(node.children[-2], objs)
        #TODO: Return logic / Continue logic
        #print inn, out
        #print 'Func', objs.keys()
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
            print 'assign -->', name
            print ' '*4, inn
            print ' '*4, out
            objs[name] = il.Func(inn, out, label=label)
            print ' '*4, objs[name]
            fobjs = objs.push()
            functions[label] = {
                'code' : Func(func, fobjs, inn, out),
                'symbols' : fobjs
            }
            code = 'Todo Func code in assign'
        else:
            raise Exception, 'Unexpected node %s' % (node.children[1].label)
        #print 'Assign', objs.keys()
        return code
    def Call(node, objs, returns):
        name = node.children[0].label
        params = (
            node.children[1].children
            if len(node.children) == 2
            else list()
        )
        assert name in objs
        typ_ = objs[name]
        assert len(typ_.inn) == len(params)
        assert len(typ_.out) == len(returns)
        code = list()
        print 'call -->', name
        print ' '*4, typ_.inn
        print ' '*4, typ_.out
        print ' '*4, typ_
        for i, p in enumerate(params):
            if p.label == 'NAME':
                pname = p.children[0].label
                ptype = objs[pname]

                print pname, ptype, typ_.inn[i]
            #il.Inst(il.IPRM, )
        print
        #print 'Call', objs.keys()
    def Block(node, objs):
        codelist = list()
        for c in node.children:
            if c.label == 'Assign':
                code = Assign(c, objs)
            elif c.label == 'Call':
                code = Call(c, objs, list())
            else:
                raise Exception, 'Unexpected node %s' % (c.label)
        #print 'Block', objs.keys()
        return code
    objs = SymbolTable(prebuilt_funcs)
    r = Block(root, objs)
    print '---'
    parents = list()
    for x,y in functions.iteritems():
        print x
        print ' '*4, 'symbols'
        parents.append(y['symbols'].parent)
        for a,b in y['symbols'].iteritems():
            print ' '*8, a, b
        print ' '*4, 'code', y['code']
    for x in parents:
        print repr(x)
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
        }/*
        add = func(d int, e int)(int) {
            x = __add(d, e)
            return x
        }
        f = func(plus func(int, int)(int), ret func(int, int)) {
            c = plus(2,3)
            continue ret(c, b)
        }
        f(add, end)*/
    ''', lexer=Lexer())
    print generate(root)
