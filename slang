#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


usage_message = \
'''usage: slang -o executable source.sl '''

extended_message = \
'''Options
    -d, debug                    Turn on debug messages (for developers)
    -h, help                     Display this message
    -i, images                   Write out images of intermediate formats
                                    writes the images to ./imgs
    -o, output                   File to write output to
    -s, asm                      Output the assembly
    -v, version                  Version information
'''

import sys, os, subprocess
from getopt import getopt, GetoptError

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

def process_input():
    ## getopt setup
    try:
        opts, args = getopt(sys.argv[1:],
            'hvo:sdi',
            ['help', 'version', 'output=', 'asm', 'debug', 'images', 'stdin'])
    except GetoptError, err:
        log(err)
        usage(error_codes['option'])

    ofile = 'a.out'
    asm = False
    images = False
    debug = False
    stdin = False
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
        elif opt in ('-i', '--images'):
            images = True
        elif opt in ('-d', '--debug'):
            debug = True
        elif opt in ('--stdin',):
            stdin = True

    if len(args) != 1 and not stdin:
        log('exactly 1 source file is required.')
        usage(error_codes['option'])

    if not stdin:
      infile = args[0]
      f = open(infile, 'r')
      source = f.read()
      f.close()
    else:
      source = sys.stdin.read()

    return ofile, asm, source, images, debug

def compile(source, ofile, asm=False, images=False, debug=False):

    AST = Parser().parse(source, lexer=Lexer())
    table, blocks, functions = il_gen.generate(AST, debug=debug)
    code = x86_gen.generate(table, blocks, functions)

    if asm:
        f = open(ofile + '.s', 'w')
        f.write(code)
        f.close()

    return code

def main():

    ofile, asm, source, images, debug = process_input()

    from conf import conf # I wait till here to import conf so when running for
                          # usage the user doesn't recieve log messages.
    code = compile(source, ofile, asm=asm, images=images, debug=debug)

    ascmd = ['as', '--32', '-o', '%s.o' % ofile]
    print
    print '[running]', ' '.join(ascmd)
    gas = subprocess.Popen(ascmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    for o in gas.communicate(code):
        if o: print '>', ' '*4, o

    ldcmd = ['ld', '-o', ofile, '-melf_i386', '-dynamic-linker', conf.dynlinker,
         conf.libc32, '%s.o' % ofile]
    print '[running]', ' '.join(ldcmd)
    ld = subprocess.Popen(ldcmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    for o in ld.communicate():
        if o: print '>', ' '*4, o

if __name__ == '__main__':
    main()
