#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from nose.tools import assert_raises
from table import Symbol, SymbolTable

def test_pushpop():
    table = SymbolTable()
    t1 = Symbol('t1', 'int', 0, 1)
    t2_1 = Symbol('t2', 'int', 0, 2)
    t3 = Symbol('t3', 'int', 0, 3)
    t2_2 = Symbol('t2', 'int', 0, 4)
    t4_1 = Symbol('t4', 'int', 0, 5)
    t4_2 = Symbol('t4', 'int', 0, 6)
    t5 = Symbol('t5', 'int', 0, 7)
    table.add(t1)
    table.add(t2_1)
    assert table == {'t1':t1, 't2':t2_1}
    table = table.push()
    assert table == {'t1':t1, 't2':t2_1}
    table.update({'t3':t3, 't2':t2_2})
    assert table == {'t1':t1, 't3':t3, 't2':t2_2}
    table = table.push()
    assert table == {'t1':t1, 't3':t3, 't2':t2_2}
    table.update({'t4':t4_1})
    assert table == {'t1':t1, 't3':t3, 't2':t2_2, 't4':t4_1}
    table = table.push()
    assert table == {'t1':t1, 't3':t3, 't2':t2_2, 't4':t4_1}
    table.update({'t4':t4_2, 't5':t5})
    assert table == {'t1':t1, 't3':t3, 't2':t2_2, 't4':t4_2, 't5':t5}
    table = table.pop()
    assert table == {'t1':t1, 't3':t3, 't2':t2_2, 't4':t4_1}
    table = table.pop()
    assert table == {'t1':t1, 't3':t3, 't2':t2_2}
    table = table.pop()
    assert table == {'t1':t1, 't2':t2_1}
    assert_raises(Exception, table.pop)
