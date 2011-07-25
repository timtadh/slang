#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from collections import MutableMapping

class SymbolTable(MutableMapping):

    def __init__(self, *args, **kwargs):
        self.table = dict()
        self.idindex = dict()
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

    def ids(self):
        if self.parent:
            return set(self.idindex.keys()) | self.parent.ids()
        return set(self.idindex.keys())

    def add(self, value):
        self[value.name] = value

    def __len__(self): return len(self.keys())
    def __contains__(self, name): return name in self.keys()

    def __iter__(self):
        for key in self.keys(): yield key

    def __setitem__(self, name, value):
        self.table[name] = value
        self.idindex[value.id] = value

    def __getitem__(self, key):
        if isinstance(key, int) or isinstance(key, long): d = self.idindex
        else: d = self.table
        if key in d:
            return d[key]
        return self.parent[key]

    def __delitem__(self, name):
        item = self[name]
        if item.name in self.table:
            del self.table[item.name]
        if item.id in self.idindex:
            del self.idindex[item.id]

    def __str__(self):
        return str(dict((k,v) for k,v in self.iteritems()))
