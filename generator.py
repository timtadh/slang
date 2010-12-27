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

class generate(object):

    def __new__(cls, root):
        self = super(generate, cls).__new__(cls)
        self.__init__()
        r = self.Block(root)
        print '---'
        parents = list()
        for x,y in self.functions.iteritems():
            print x
            print ' '*4, 'symbols'
            parents.append(y['symbols'].parent)
            for a,b in y['symbols'].iteritems():
                print ' '*8, a, b
            print ' '*4, 'code', y['code']
        for x in parents:
            print repr(x)
        print '---'
        for x,y in self.objs.iteritems():
            print x, y
        print '---'
        return r, self.functions

    def __init__(self):
        self.functions = dict()
        self.fcount = 0
        self.objs = SymbolTable(prebuilt_funcs)


    def Block(self, node):
        codelist = list()
        for c in node.children:
            if c.label == 'Assign':
                code = self.Assign(c)
            elif c.label == 'Call':
                code = self.Call(c, list())
            else:
                raise Exception, 'Unexpected node %s' % (c.label)
        #print 'Block', objs.keys()
        return code

    def Call(self, node, returns):
        name = node.children[0].label
        params = (
            node.children[1].children
            if len(node.children) == 2
            else list()
        )
        assert name in self.objs
        typ_ = self.objs[name]
        assert len(typ_.inn) == len(params)
        assert len(typ_.out) == len(returns)
        code = list()
        print 'call -->', name
        print ' '*4, typ_.inn
        print ' '*4, typ_.out
        print ' '*4, typ_
        for i, p in enumerate(params):
            if p.label == 'NAME':
                lname = p.children[0].label
                ltype = self.objs[lname]
                print lname,
            elif p.label == 'INT':
                ltype = il.Const(p.children[0].label)
                print ltype.value,
            rtype = typ_.inn[i]['type']
            new_type = il.coerce(ltype, rtype)
            print ltype, rtype, new_type
            #il.Inst(il.IPRM, )
        print
        #print 'Call', objs.keys()

    def Assign(self, node):
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
            label = 'func_%d' % self.fcount; self.fcount += 1
            inn, out = self.Params(func)
            print 'assign -->', name
            print ' '*4, inn
            print ' '*4, out
            self.objs[name] = il.Func(inn, out, label=label)
            print ' '*4, self.objs[name]
            self.objs = self.objs.push()
            self.functions[label] = {
                'code' : self.Func(func, inn, out),
                'symbols' : self.objs
            }
            self.objs = self.objs.pop()
            code = 'Todo Func code in assign'
        else:
            raise Exception, 'Unexpected node %s' % (node.children[1].label)
        #print 'Assign', objs.keys()
        return code

    def Func(self, node, inn, out):
        for obj in inn:
            self.objs[obj['name']] = obj['type']
        #print
        #print
        #TODO: parameter logic
        block = self.Block(node.children[-2])
        #TODO: Return logic / Continue logic
        #print inn, out
        #print 'Func', objs.keys()
        return block

    def Type(self, node):
        if node.label == 'IntType':
            return il.Int()
        elif node.label == 'FuncType':
            inn = list()
            out = list()
            for c in node.children:
                if c.label == 'Takes':
                    for t in c.children:
                        inn.append({'name':None, 'type':self.Type(t)})
                elif c.label == 'Returns':
                    for t in c.children:
                        out.append(self.Type(t))
            return il.Func(inn, out)

    def Params(self, node):
        inn = list()
        out = list()
        for c in node.children:
            if c.label == 'Takes':
                for d in c.children:
                    inn.append({
                        'name': d.children[0].label,
                        'type': self.Type(d.children[1])
                    })
            elif c.label == 'Returns':
                for d in c.children:
                    out.append(self.Type(d))
        print '----->', inn, out
        return inn, out

    # ------------------------------------------------------------------------ #


if __name__ == '__main__':

    root = Parser().parse('''
        end = func(r1 int, r2 int) {
            print(1)
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
