#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import os, subprocess

from frontend.sl_parser import Parser, Lexer
import cf, il, df
import abstract, example
import nose

@nose.tools.raises(TypeError)
def t_abstract_init_fail():
    abstract.DataFlowAnalyzer()

def t_example_init():
    example.ReachingDefintions()
