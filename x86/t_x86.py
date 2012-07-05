#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, cStringIO, subprocess, traceback

from conf import conf
from frontend.sl_parser import Parser, Lexer
#from table import SymbolTable
import il
from il import il_gen
import x86_gen, x86
import nose

def run(s):
    #out = cStringIO.StringIO()
    try:
        code = x86_gen.generate(*il_gen.generate(Parser().parse(s, lexer=Lexer()), debug=True))
        print code
        gas = subprocess.Popen(['as', '--32', '-o', 'exe.o'], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        print gas.communicate(code)
        ld = subprocess.Popen(['ld', '-o', 'exe', '-melf_i386', '-dynamic-linker', conf.dynlinker,
             conf.libc32, 'exe.o'], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
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

def t_version():
    print sys.version
    print x86.reg.type
    #assert False

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
        var f = func() {
            print 9
            return
        }
        f()
        ''').rstrip('\n')
    #raise Exception

def t_func_call_simple_with_1_param():
    #raise nose.SkipTest
    assert str(4) == run('''
        var f = func(a) {
            print a
            return
        }
        f(4)
        ''').rstrip('\n')
    #raise Exception

def t_func_call_simple_with_2_params():
    #raise nose.SkipTest
    assert str(1) == run('''
        var f = func(a, b) {
            print a - b
            return
        }
        f(5, 4)
        ''').rstrip('\n')
    #raise Exception

def t_func_call_return():
    #raise nose.SkipTest
    assert str(1) == run('''
        var f = func() { return 1 }
        print f()
        ''').rstrip('\n')
    #raise Exception

def t_func_call():
    #raise nose.SkipTest
    assert str(5 / 4 * 2 + 10 - 5 * 2 / 3) == run('''
        var f = func() { return 5 / 4 * 2 + 10 - 5 * 2 / 3 }
        print f()
        ''').rstrip('\n')
    #raise Exception

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
    #raise nose.SkipTest
    assert str(4) == run('''
        var sub = func(a, b) {
            var _sub = func() {
                return a - b
            }
            return _sub()
        }
        print sub(5+7, 8)
        ''').rstrip('\n')

def t_func_params_stack_modify_upper():
    #raise nose.SkipTest
    assert str(4) == run('''
        var sub = func(a, b) {
            var c = 0
            var _sub = func() {
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
        var sub = func(a, b) {
            var c = 0
            var _sub = func() {
                c = a - b
                return
            }
            _sub()
            return c
        }
        var call = func(f, a, b) {
            return f(a, b)
        }
        print call(sub, 5+7, 8)
        ''').rstrip('\n')

def t_func_params_stack_modify_upper_func_pointer_var_redecl():
    #raise nose.SkipTest
    assert ['4', '4', '1'] == run('''
        var sub = func(a, b) {
            var c = 0
            var _sub = func() {
                c = 1 // modifies upper c.
                var c = a - b // creates a new c.
                print c
                // var c = 5 // causes type error do to var redeclare in same scope
                print c
                return
            }
            _sub()
            return c
        }
        var call = func(f, a, b) {
            return f(a, b)
        }
        print call(sub, 5+7, 8)
        ''').rstrip('\n').split('\n')
    #assert False

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

def t_if_not():
    #raise nose.SkipTest
    assert str(1) == run('''
        if (!1 > 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (!1 < 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')

def t_if_and():
    #raise nose.SkipTest
    assert str(1) == run('''
        if (1 < 2 && 3 < 4) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (1 > 2 && 3 < 4) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (1 < 2 && 3 > 4) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (1 > 2 && 3 > 4) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')

def t_if_or():
    #raise nose.SkipTest
    assert str(1) == run('''
        if (1 < 2 || 3 < 4) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if (1 > 2 || 3 < 4) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if (1 < 2 || 3 > 4) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (1 > 2 || 3 > 4) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')


def t_if_and_nest_or():
    #raise nose.SkipTest
    assert str(1) == run('''
        if (1 < 2 && (3 < 4 || 5 < 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if (1 < 2 && (3 > 4 || 5 < 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if (1 < 2 && (3 < 4 || 5 > 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (1 < 2 && (3 > 4 || 5 > 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (1 > 2 && (3 < 4 || 5 < 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (1 > 2 && (3 > 4 || 5 < 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (1 > 2 && (3 < 4 || 5 > 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (1 > 2 && (3 > 4 || 5 > 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if ((3 < 4 || 5 < 6) && 1 < 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if ((3 < 4 || 5 > 6) && 1 < 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if ((3 > 4 || 5 < 6) && 1 < 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if ((3 > 4 || 5 > 6) && 1 < 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if ((3 < 4 || 5 < 6) && 1 > 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if ((3 < 4 || 5 > 6) && 1 > 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if ((3 > 4 || 5 < 6) && 1 > 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if ((3 > 4 || 5 > 6) && 1 > 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')

def t_if_or_nest_and():
    #raise nose.SkipTest
    assert str(1) == run('''
        if (1 < 2 || (3 < 4 && 5 < 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if (1 < 2 || (3 > 4 && 5 < 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if (1 < 2 || (3 < 4 && 5 > 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if (1 < 2 || (3 > 4 && 5 > 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if (1 > 2 || (3 < 4 && 5 < 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (1 > 2 || (3 > 4 && 5 < 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (1 > 2 || (3 < 4 && 5 > 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (1 > 2 || (3 > 4 && 5 > 6)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if ((3 < 4 && 5 < 6) || 1 < 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if ((3 < 4 && 5 > 6) || 1 < 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if ((3 > 4 && 5 < 6) || 1 < 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if ((3 > 4 && 5 > 6) || 1 < 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if ((3 < 4 && 5 < 6) || 1 > 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if ((3 < 4 && 5 > 6) || 1 > 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if ((3 > 4 && 5 < 6) || 1 > 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if ((3 > 4 && 5 > 6) || 1 > 2) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')

def t_if_not_and():
    #raise nose.SkipTest
    assert str(1) == run('''
        if (!(1 > 2 && 3 > 4)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if (!(1 < 2 && 3 > 4)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(1) == run('''
        if (!(1 > 2 && 3 < 4)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (!(1 < 2 && 3 < 4)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')

def t_if_not_or():
    #raise nose.SkipTest
    assert str(1) == run('''
        if (!(1 > 2 || 3 > 4)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (!(1 < 2 || 3 > 4)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (!(1 > 2 || 3 < 4)) {
            print 1
        } else {
            print 2
        }
        ''').rstrip('\n')
    assert str(2) == run('''
        if (!(1 < 2 || 3 < 4)) {
            print 1
        } else {
            print 2
        }
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
    assert str(0) ==  run('''
        var f = func(x) {
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

def t_fib():
    assert str(55) == run('''
      var fib = func(x) {
          var c
          if (x > 1) {
              c = fib(x-1) + fib(x-2)
          } else {
              if (x == 1) {
                  c = 1
              } else {
                  c = 0
              }
          }
          return c
      }
      print fib(10)
        ''').rstrip('\n')

def t_fib_while():
    assert str(55) == run('''
      var fib = func(x) {
          var prev = 0
          var cur = 1
          var i = 1
          if x == 0 {
              cur = 0
          } else {
              while i < x {
                  var next = prev + cur
                  prev = cur
                  cur = next
                  i = i + 1
              }
          }
          return cur
      }
      print fib(10)
        ''').rstrip('\n')
