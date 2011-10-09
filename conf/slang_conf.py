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
        super(SlangConfig, self).__init__(*args, **kwargs)


valid_locs = [loc for loc in [HOME_LOC, DEFAULT_LOC] if os.path.exists(loc)]

if not valid_locs:
    log.warn('No Config File Found')
    log.warn('Generating new default at %s' % DEFAULT_LOC)
    loc = DEFAULT_LOC
else:
    loc = valid_locs[0]

conf = SlangConfig(SCHEMA, loc)
