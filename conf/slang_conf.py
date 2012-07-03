#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, json, logging
import cStringIO as sio

import conf
import log_conf
log = logging.getLogger('srvconf')

HOME_DIR = os.environ.get('HOME')
if HOME_DIR == None:
    HOME_DIR = str()
DEFAULT_LOC = os.path.join(os.path.dirname(__file__), 'slangrc')
HOME_LOC = os.path.join(HOME_DIR, ".slangrc")


SCHEMA = {
    'dynlinker': 'str', # '/lib/ld-linux.so.2',
    'libc32': 'str', # '/lib32/libc.so.6',
}

class SlangConfig(conf.BaseConfig):


    def __init__(self, *args, **kwargs):
        self.__check_defaults()
        super(SlangConfig, self).__init__(*args, **kwargs)

    def __check_defaults(self):
        if not self._d['dynlinker'] or not self._d['libc32']:
            print
            print (
                "You don't seem to have Slang configured yet! I have \n"
                "automatically created a configuration file for you so no \n"
                "sweat. But, you need to enter some values for me."
            )
            print
            while not self._d['dynlinker']:
                dlink = raw_input(
                  'We need a dynamic linker, a possible location for the '
                  'linker is /lib/ld-linux.so.2\n'
                  'Where is your dynamic linker located? ')
                if os.path.exists(dlink):
                    self._d['dynlinker'] = dlink
                else:
                    print ' '*4, 'No it is not. I checked, there is nothing there.'
            if not self._d['dynlinker']: print
            while not self._d['libc32']:
                libc = raw_input(
                  'We need a 32 bit libc. A possible location for that is '
                  '/lib32/libc.so.6\n'
                  'Where is your *32 bit* libc located? ')
                if os.path.exists(libc):
                    self._d['libc32'] = libc
                else:
                    print ' '*4, 'No it is not. I checked, there is nothing there.'
            if not self._d['libc32']: print


valid_locs = [loc for loc in [HOME_LOC, DEFAULT_LOC] if os.path.exists(loc)]

if not valid_locs:
    log.warn('No Config File Found')
    log.warn('Generating new default at %s' % DEFAULT_LOC)
    loc = DEFAULT_LOC
else:
    loc = valid_locs[0]

conf = SlangConfig(SCHEMA, loc)
