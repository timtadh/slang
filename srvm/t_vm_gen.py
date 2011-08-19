#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import cStringIO

from frontend.sl_parser import Parser, Lexer
#from table import SymbolTable
import il
from il import il_gen
import vm_gen, vm
import nose

def run(s):
    out = cStringIO.StringIO()
    vm.run(vm_gen.generate(*il_gen.generate(Parser().parse(s, lexer=Lexer()))), out)
    r = out.getvalue()
    del out
    return r

def t_expr_const():
    assert '2' == run('print 2').rstrip('\n')

def t_expr_ops():
    #raise nose.SkipTest
    assert '6' == run('print 2*3').rstrip('\n')
    assert '6' == run('print 1+2+3').rstrip('\n')
    assert '6' == run('print 9-3').rstrip('\n')
    assert '6' == run('print 12/2').rstrip('\n')

def t_expr_compound():
    #raise nose.SkipTest
    assert str(4*3/2) == run('print 4*3/2').rstrip('\n')
    assert str(4/2*3) == run('print 4/2*3').rstrip('\n')
    assert str((3+9)*4/8) == run('print (3+9)*4/8').rstrip('\n')
    assert str(((9-3)+(5-3))/2 + 2) == run('print ((9-3)+(5-3))/2 + 2').rstrip('\n')
    assert str(5 * 4 / 2 - 10 + 5 - 2 + 3) == run('print 5 * 4 / 2 - 10 + 5 - 2 + 3').rstrip('\n')
    assert str(5 / 4 * 2 + 10 - 5 * 2 / 3) == run('print 5 / 4 * 2 + 10 - 5 * 2 / 3').rstrip('\n')

def t_func_call():
    #raise nose.SkipTest
    assert str(5 / 4 * 2 + 10 - 5 * 2 / 3) == run('''
        var f = func() { return 5 / 4 * 2 + 10 - 5 * 2 / 3 }
        print f()
        ''').rstrip('\n')
    #assert False

def t_func_uppernames():
    #raise nose.SkipTest
    assert str(5 / 4 * 2 + 10 - 5 * 2 / 3) == run('''
        var g = func() {
            var g1 = func() { return g2() }
            var g2 = func() { return g3() }
            var g3 = func() { return h() }
            return g1()
        }
        var h = func() { return f() }
        var f = func() { return 5 / 4 * 2 + 10 - 5 * 2 / 3 }
        print g()
        ''').rstrip('\n')
    #assert False

def t_func_pointers():
    #raise nose.SkipTest
    assert str(5 / 4 * 2 + 10 - 5 * 2 / 3) == run('''
        var f = func() { return 5 / 4 * 2 + 10 - 5 * 2 / 3 }
        var g = func(h) { return h() }
        print g(f)
        ''').rstrip('\n')

def t_func_params_simple():
    #raise nose.SkipTest
    assert str(4) == run('''
        var sub = func(a, b) { return a - b }
        print sub(5+7, 8)
        ''').rstrip('\n')

def t_func_params_stack():
    raise nose.SkipTest
    ## This tests currently fails because the code generator is not setup to do this properly.
    ## It may require a non-trivial re-write to get this to work, because none of the operators
    ## check if the referenced symbol is in the current block scope (read stack frame) of the
    ## function context. When it is out of scope it should look up the stack for the appropriate
    ## frame.
    assert str(4) == run('''
        var sub = func(a, b) {
            var _sub = func() {
                return a - b
            }
            return _sub()
        }
        print sub(5+7, 8)
        ''').rstrip('\n')

def t_if():
    #raise nose.SkipTest
    assert str(2) == run('''
        if (1 > 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if (1 < 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')


def t_if_set():
    #raise nose.SkipTest
    assert str(2) == run('''
        var a
        if (1 > 2) {
            a = 1
        } else {
            a = 2
        }
        print a
        ''').rstrip('\n')
    assert str(1) == run('''
        var a
        if (1 < 2) {
            a = 1
        } else {
            a = 2
        }
        print a
        ''').rstrip('\n')
    assert str(1) == run('''
        var a = 2
        if (1 < 2) {
            a = 1
        }
        print a
        ''').rstrip('\n')

def t_lone_expr():
    #raise nose.SkipTest
    assert str(5 / 4 * 2 + 10 - 5 * 2 / 3) == run('''
        var a = func() {
            var f = func() { return 5 / 4 * 2 + 10 - 5 * 2 / 3 }
            var g = func(h) { return h() }
            print g(f)
            return
        }
        a()
        ''').rstrip('\n')

def t_bb():
    #raise nose.SkipTest
    assert str(5) == run('''
        var f = func(a, b) {
            var c
            if (a > b) {
                c = a
            } else {
                c = b
            }
            return c
        }
        print f(1, 5)
        ''').rstrip('\n')
    #assert False
    assert str(10) == run('''
        var f = func(a, b) {
            var c
            if (a > b) {
                c = a
            } else {
                c = b
            }
            return c
        }
        print f(10, 5)
        ''').rstrip('\n')


def t_recursive():
    #raise nose.SkipTest
    assert str(0) == run('''
        var f = func(x) {
            var c
            if (x > 0) {
                c = f(x-1)
            } else {
                c = x
            }
            return c
        }
        print f(10)
        ''').rstrip('\n')


def t_nested_if():
    #raise nose.SkipTest
    print run('''
        var f = func(x) {
            print x
            var c
            if (x > 0) {
                if (x/2 + x/2 == x) { // then it is even
                    c = f(x+1)
                } else {
                    c = f(x-3)
                }
            } else {
                if (x == 0) {
                    c = x
                } else {
                    c = 10
                }
            }
            return c
        }
        print f(10)
        ''').rstrip('\n')
    #assert False
