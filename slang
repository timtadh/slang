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
import cf, df

CWD = os.environ.get('PWD', os.getcwd())
RELEASE = 'slang 0.01'
img_dir = './imgs'

error_codes = {
    'usage':1,
    'compile_error':2,
    'option':3,
}

def log(*msgs):
    for msg in msgs:
        print msg,
    print

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
            [
              'help', 'version', 'output=', 'asm', 'debug', 'images', 'stdin',
              'dataflow',
            ]
        )
    except GetoptError, err:
        log(err)
        usage(error_codes['option'])

    ofile = 'a.out'
    asm = False
    images = False
    debug = False
    stdin = False
    dataflow = False
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
        elif opt in ('--dataflow',):
            dataflow = True

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

    return ofile, asm, source, images, debug, dataflow

def dot(name, dotty, AST=None):
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    if AST:
        ast = os.path.join(img_dir, name) + '.ast'
        f = open(ast, 'w')
        f.write(AST)
        f.close()

    dot = os.path.join(img_dir, name) + '.dot'
    plain = os.path.join(img_dir, name) + '.plain'
    png = os.path.join(img_dir, name) + '.png'

    f = open(dot, 'w')
    f.write(dotty)
    f.close()

    p = subprocess.Popen(['dot', '-Tplain', '-o', plain], stdin=subprocess.PIPE)
    p.stdin.write(dotty + '\0')
    p.stdin.close()
    p.wait()

    p = subprocess.Popen(['dot', '-Tpng', '-o', png], stdin=subprocess.PIPE)
    p.stdin.write(dotty + '\0')
    p.stdin.close()
    p.wait()

def compile(source, ofile, asm=False, images=False, debug=False, dataflow=False):

    name = os.path.splitext(os.path.basename(ofile))[0]

    ast = Parser().parse(source, lexer=Lexer())
    table, blocks, functions = il_gen.generate(ast, debug=debug)
    if images or dataflow:
        cf.analyze(table, blocks, functions, debug=False)
    if images:
        dot('ast.%s'%name, ast.dotty(), str(ast))
        for funcname in functions:
            dot('blks.%s.%s'%(name,funcname), functions[funcname].entry.dotty())
            dot('cf.%s.%s'%(name,funcname), functions[funcname].tree.dotty())
    if dataflow:
        df.analyze(df.reachdef.ReachingDefinitions, functions)
        df.analyze(df.livevar.LiveVariable, functions, attach_method=True)
        df.analyze(df.taint.TaintFlow, functions, attach_method=True)
        log('reachdef')
        for fname, f in functions.iteritems():
            log(' '*2, fname)
            for blk in f.blks:
                log(' '*4, blk.name)
                log(' '*8, ' in', f.df['reachdef'].inn[blk.name])
                log(' '*8, 'out', f.df['reachdef'].out[blk.name])
        log('livevar')
        for fname, f in functions.iteritems():
            log(' '*2, fname)
            for blk in f.blks:
                log(' '*4, blk.name)
                log(' '*8, ' in', f.livetypes(blk.name, dir='inn'))
                log(' '*8, 'out', f.livetypes(blk.name, dir='out'))
        log('taint')
        for fname, f in functions.iteritems():
            log(' '*2, fname)
            for blk in f.blks:
                log(' '*4, blk.name)
                log(' '*8, ' in', f.taints(blk.name, 'inn'))
                log(' '*8, 'out', f.taints(blk.name, 'out'))
    code = x86_gen.generate(table, blocks, functions)

    if asm:
        f = open(ofile + '.s', 'w')
        f.write(code)
        f.close()

    return code

def main():

    ofile, asm, source, images, debug, dataflow = process_input()

    from conf import conf # I wait till here to import conf so when running for
                          # usage the user doesn't recieve log messages.
    code = compile(source, ofile, asm=asm, images=images, debug=debug,
            dataflow=dataflow)

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
