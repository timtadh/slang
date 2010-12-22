#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from collections import MutableMapping

class SymbolTable(MutableMapping):

    def __init__(self, *args, **kwargs):
        self.table = dict()
        self.parent = kwargs.pop('parent') if 'parent' in kwargs else dict()
        self.update(*args, **kwargs)

    def push(self):
        return SymbolTable(parent=self)

    def pop(self):
        if isinstance(self.parent, dict):
            raise Exception, 'SymbolTable has no parent, stack empty'
        return self.parent

    def keys(self):
        keys = set(self.table.keys()) | set(self.parent.keys())
        return keys

    def __len__(self): return len(self.keys())
    def __contains__(self, name): return name in self.keys()

    def __iter__(self):
        for key in self.keys(): yield key

    def __setitem__(self, name, value):
        self.table[name] = value

    def __getitem__(self, name):
        if name in self.table:
            return self.table[name]
        return self.parent[name]

    def __delitem__(self, name):
        if name not in self.keys():
            raise KeyError, 'Name "%s" not in SymbolTable' % (name)
        if name in self.table:
            del self.table[name]

    def __str__(self):
        return str(dict((k,v) for k,v in self.iteritems()))
