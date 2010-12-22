#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from nose.tools import assert_raises
from table import SymbolTable

def test_pushpop():
    t = SymbolTable({1:2, 3:4})
    assert t == {1:2, 3:4}
    t = t.push()
    assert t == {1:2, 3:4}
    t.update({3:5, 5:6})
    assert t == {1:2, 3:5, 5:6}
    t = t.push()
    assert t == {1:2, 3:5, 5:6}
    t.update({5:7, 7:8})
    assert t == {1:2, 3:5, 5:7, 7:8}
    t = t.pop()
    assert t == {1:2, 3:5, 5:6}
    t = t.pop()
    assert t == {1:2, 3:4}
    assert_raises(Exception, t.pop)
