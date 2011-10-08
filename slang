#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


usage_message = \
'''usage: slang -o executable source.sl '''

extended_message = usage_message

import sys, os, subprocess
from getopt import getopt, GetoptError

from conf import conf
from frontend.sl_parser import Parser, Lexer
from il import il_gen
from x86 import x86_gen

CWD = os.environ.get('PWD', os.getcwd())
RELEASE = 'slang 0.01'

error_codes = {
    'usage':1,
    'compile_error':2,
    'option':3,
}

def log(msg):
    print msg

def usage(code=None):
    '''Prints the usage and exits with an error code specified by code. If code
    is not given it exits with error_codes['usage']'''
    log(usage_message)
    if code is None:
        log(extended_message)
        code = error_codes['usage']
    sys.exit(code)


def main():

    ## getopt setup
    try:
        opts, args = getopt(sys.argv[1:], 'hvo:s', ['help', 'version', 'output=', 'asm'])
    except GetoptError, err:
        log(err)
        usage(error_codes['option'])

    ofile = 'a.out'
    asm = False
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-v', '--version'):
            log(RELEASE)
            sys.exit(error_codes['version'])
        elif opt in ('-o', '--output'):
            ofile = arg
        elif opt in ('-s', '--asm'):
            asm = True

    if len(args) != 1:
        log('exactly 1 source file is required.')
        usage(error_codes['option'])

    infile = args[0]

    f = open(infile, 'r')
    source = f.read()
    f.close()

    code = x86_gen.generate(*il_gen.generate(Parser().parse(source, lexer=Lexer()), debug=True))
    if asm:
        f = open(ofile + '.s', 'w')
        f.write(code)
        f.close()
    #print code
    gas = subprocess.Popen(['as', '--32', '-o', '%s.o' % ofile], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    print gas.communicate(code)
    ldcmd = ['ld', '-o', ofile, '-melf_i386', '-dynamic-linker', conf.dynlinker,
         conf.libc32, '%s.o' % ofile]
    print ' '.join(ldcmd)
    ld = subprocess.Popen(ldcmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    print ld.communicate()

if __name__ == '__main__':
    main()
