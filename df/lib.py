#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import collections

def DFS(root, attr):
    cache_attr = '__reachable_from_%s' % attr
    if hasattr(root, cache_attr):
        return set(getattr(root, cache_attr))

    visited = set()
    stack = collections.deque()
    stack.append(root)

    while stack:
        blk = stack.pop()
        visited.add(blk.name)
        for b in getattr(blk, attr):
            if b.name not in visited:
                stack.append(b)

    ret = visited - set([root.name])
    setattr(root, cache_attr, set(ret))
    return ret
