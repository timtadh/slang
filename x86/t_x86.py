#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, cStringIO, subprocess, traceback

from frontend.sl_parser import Parser, Lexer
#from table import SymbolTable
import il
from il import il_gen
import x86_gen
import nose

def run(s):
    #out = cStringIO.StringIO()
    try:
        code = x86_gen.generate(*il_gen.generate(Parser().parse(s, lexer=Lexer()), debug=True))
        print code
        gas = subprocess.Popen(['as', '--32', '-o', 'exe.o'], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        print gas.communicate(code)
        ld = subprocess.Popen(['ld', '-o', 'exe', '-melf_i386', '-dynamic-linker', '/lib/ld-linux.so.2', '/lib32/libc.so.6', 'exe.o'], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        print ld.communicate()
        exe = subprocess.Popen(['./exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret, err = exe.communicate()
        print '>', (ret, err)
    except Exception, e:
        print e
        traceback.print_exc(file=sys.stdout)
        ret = 'fail'
        err = e
    finally:
        #os.unlink('exe.o')
        #os.unlink('exe')
        pass

    if err:
        ret = 'fail'
        print err

    print '---->', ret
    return ret

def t_expr_const():
    #raise nose.SkipTest
    assert '2' == run('print 2').rstrip('\n')
    #raise Exception

def t_expr_ops():
    #raise nose.SkipTest
    assert '6' == run('print 9-3').rstrip('\n')
    assert '6' == run('print 2*3').rstrip('\n')
    assert '6' == run('print 1+2+3').rstrip('\n')
    assert '6' == run('print 12/2').rstrip('\n')

def t_expr_compound():
    #raise nose.SkipTest
    assert str(4*3/2) == run('print 4*3/2').rstrip('\n')
    assert str(4/2*3) == run('print 4/2*3').rstrip('\n')
    assert str((3+9)*4/8) == run('print (3+9)*4/8').rstrip('\n')
    assert str(((9-3)+(5-3))/2 + 2) == run('print ((9-3)+(5-3))/2 + 2').rstrip('\n')
    assert str(5 * 4 / 2 - 10 + 5 - 2 + 3) == run('print 5 * 4 / 2 - 10 + 5 - 2 + 3').rstrip('\n')
    assert str(5 / 4 * 2 + 10 - 5 * 2 / 3) == run('print 5 / 4 * 2 + 10 - 5 * 2 / 3').rstrip('\n')

def t_func_call_simple():
    #raise nose.SkipTest
    assert str(5 / 4 * 2 + 10 - 5 * 2 / 3) == run('''
        f = func() {
            print 9
            return
        }
        f()
        ''').rstrip('\n')
    #raise Exception

def t_func_call_simple_with_1_param():
    #raise nose.SkipTest
    assert str(4) == run('''
        f = func(a) {
            print a
            return
        }
        f(4)
        ''').rstrip('\n')
    #raise Exception

def t_func_call_simple_with_2_params():
    #raise nose.SkipTest
    assert str(1) == run('''
        f = func(a, b) {
            print a - b
            return
        }
        f(5, 4)
        ''').rstrip('\n')
    #raise Exception

def t_func_call_return():
    #raise nose.SkipTest
    assert str(1) == run('''
        f = func() { return 1 }
        print f()
        ''').rstrip('\n')
    #raise Exception

def t_func_call():
    #raise nose.SkipTest
    assert str(5 / 4 * 2 + 10 - 5 * 2 / 3) == run('''
        f = func() { return 5 / 4 * 2 + 10 - 5 * 2 / 3 }
        print f()
        ''').rstrip('\n')
    #raise Exception

def t_func_uppernames():
    #raise nose.SkipTest
    assert str(5 / 4 * 2 + 10 - 5 * 2 / 3) == run('''
        g = func() {
            g1 = func() { return g2() }
            g2 = func() { return g3() }
            g3 = func() { return h() }
            return g1()
        }
        h = func() { return f() }
        f = func() { return 5 / 4 * 2 + 10 - 5 * 2 / 3 }
        print g()
        ''').rstrip('\n')

def t_func_pointers():
    #raise nose.SkipTest
    assert str(5 / 4 * 2 + 10 - 5 * 2 / 3) == run('''
        f = func() { return 5 / 4 * 2 + 10 - 5 * 2 / 3 }
        g = func(h) { return h() }
        print g(f)
        ''').rstrip('\n')

def t_func_params_simple():
    #raise nose.SkipTest
    assert str(4) == run('''
        sub = func(a, b) { return a - b }
        print sub(5+7, 8)
        ''').rstrip('\n')

def t_func_params_stack():
    #raise nose.SkipTest
    assert str(4) == run('''
        sub = func(a, b) {
            _sub = func() {
                return a - b
            }
            return _sub()
        }
        print sub(5+7, 8)
        ''').rstrip('\n')

def t_func_params_stack_modify_upper():
    #raise nose.SkipTest
    assert str(4) == run('''
        sub = func(a, b) {
            c = 0
            _sub = func() {
                c = a - b
                return
            }
            _sub()
            return c
        }
        print sub(5+7, 8)
        ''').rstrip('\n')

def t_func_params_stack_modify_upper_func_pointer():
    #raise nose.SkipTest
    assert str(4) == run('''
        sub = func(a, b) {
            c = 0
            _sub = func() {
                c = a - b
                return
            }
            _sub()
            return c
        }
        call = func(f, a, b) {
            return f(a, b)
        }
        print call(sub, 5+7, 8)
        ''').rstrip('\n')

def t_if():
    raise nose.SkipTest
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
    raise nose.SkipTest
    assert str(2) == run('''
        if (1 > 2) {
            a = 1
        } else {
            a = 2
        }
        print a
        ''').rstrip('\n')
    assert str(1) == run('''
        if (1 < 2) {
            a = 1
        } else {
            a = 2
        }
        print a
        ''').rstrip('\n')
    assert str(1) == run('''
        a = 2
        if (1 < 2) {
            a = 1
        }
        print a
        ''').rstrip('\n')

def t_lone_expr():
    raise nose.SkipTest
    assert str(5 / 4 * 2 + 10 - 5 * 2 / 3) == run('''
        a = func() {
            f = func() { return 5 / 4 * 2 + 10 - 5 * 2 / 3 }
            g = func(h) { return h() }
            print g(f)
            return
        }
        a()
        ''').rstrip('\n')

def t_bb():
    raise nose.SkipTest
    assert str(5) == run('''
        f = func(a, b) {
            if (a > b) {
                c = a
            } else {
                c = b
            }
            return c
        }
        print f(1, 5)
        ''').rstrip('\n')
    assert str(10) == run('''
        f = func(a, b) {
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
    raise nose.SkipTest
    assert str(0) == run('''
        f = func(x) {
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
    raise nose.SkipTest
    assert str(0) ==  run('''
        f = func(x) {
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
