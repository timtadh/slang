#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, json, logging
import cStringIO as sio

import log_conf
log = logging.getLogger('conf')

def encode(d):
    new = dict()
    for k,v in d.iteritems():
        if isinstance(v, list):
            l = list()
            for i in v:
                if isinstance(i, unicode):
                    l.append(i.encode('utf-8'))
                else:
                    l.append(i)
            v = l
        if isinstance(k, unicode): k = k.encode('utf-8')
        if isinstance(v, unicode): v = v.encode('utf-8')
        new[k] = v
    return new


def make_list_get(d, key):
    def get(self):
        return [
            Section(i) for i in d[key] if isinstance(i, dict)
        ] + [
            i for i in d[key] if not isinstance(i, dict)
        ]
    return get
def make_sec_get(d, key):
    def get(self):
        return Section(d[key])
    return get
def make_val_get(d, key):
    def get(self):
        return d[key]
    return get
def _set(self,k,v): raise RuntimeError, 'Operation Not Supported'
def _del(self): raise RuntimeError, 'Operation Not Supported'

class Section(object):

    def __init__(self, d):

        for k,v in d.iteritems():
            if not (isinstance(v, dict) or isinstance(v, list)):
                p = property(make_val_get(d, k),_set,_del,
                    'Property for interacting with "%s"' % k)
            elif isinstance(v, dict):
                p = property(make_sec_get(d, k),_set,_del,
                    'Property for interacting with "%s"' % k)
            elif isinstance(v, list):
                p = property(make_list_get(d, k),_set,_del,
                    'Property for interacting with "%s"' % k)
            object.__setattr__(self, k, p)

    def __repr__(self):
        l = list()
        for name in dir(self):
            a = object.__getattribute__(self, name)
            if type(a) == property: l.append((name, str(a.fget(self))))

        return str(dict(l))

    def __getattribute__(self, name):
        if type(object.__getattribute__(self, name)) == property:
            return object.__getattribute__(self, name).fget(self)
        return object.__getattribute__(self, name)


class BaseConfig(object):

    def __new__(cls, schema, file_path):
        self = super(BaseConfig, cls).__new__(cls)
        self.schema = schema
        self.file_path = file_path
        log.info('Using config file at %s' % file_path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                try:
                    self._d = json.load(f, object_hook=encode)
                    self._matches(self._d)
                except ValueError, e:
                    log.exception(
                        "The config file at '%s' appears to be corrupted." %
                        file_path
                    )
                    sys.exit(1)
        else:
            self._d = self._skeleton()
            log.debug(self._d)
        return self

    def __init__(self, schema, file_path):
        self.write_conf()
        self._expose_dict()

    def __getattribute__(self, name):
        if type(object.__getattribute__(self, name)) == property:
            return object.__getattribute__(self, name).fget(self)
        return object.__getattribute__(self, name)

    ## public methods ## ##
    def write_conf(self, file_path=None):
        self._matches(self._d)
        if file_path is None: file_path = self.file_path
        with open(file_path, 'wb') as f:
            json.dump(self._d, f, indent=4)

    ## ## private methods ## ##
    def _expose_dict(self):
        d = self._d
        for k,v in self._d.iteritems():
            if not hasattr(self,k) and not (isinstance(v, dict) or isinstance(v, list)):
                p = property(make_val_get(d, k))
                setattr(self, k, p)
            elif not hasattr(self,k) and isinstance(v, dict):
                p = property(make_sec_get(d, k))
                setattr(self, k, p)
            elif not hasattr(self,k) and isinstance(v, list):
                p = property(make_list_get(d, k))
                setattr(self, k, p)
            else:
                # the user overroad the default property
                pass

    def _skeleton(self):
        '''produce a skeleton dictionary from the schema (with nones for values)'''
        def getdefault(s):
            '''transform a string into a type'''
            if   s == 'str'  : return str()
            elif s == 'int'  : return 0
            elif s == 'float': return 0.0
            elif s == 'bool' : return False
            raise Exception, 'Type %s unsupported' % s
        def proc(t):
            if   isinstance(t, dict):
                return procdict(t, dict())
            elif isinstance(t, list):
                return list()
            else:
                return getdefault(t)
        def procdict(t, d):
            if '__undefinedkeys__' in t:
                return dict()
            for k,v in t.iteritems():
                d[k] = proc(v)
            return d
        return procdict(self.schema, dict())

    def _matches(self, d, allow_none=False):
        '''
        Assert that d matches the schema
        @param d = the dictionary
        @param allow_none = allow Nones in d
        '''
        def gettype(s):
            '''transform a string into a type'''
            if   s == 'str'  : return str
            elif s == 'list' : return list
            elif s == 'dict' : return dict
            elif s == 'int'  : return int
            elif s == 'float': return float
            elif s == 'bool' : return bool
            raise Exception, 'Type %s unsupported' % s
        def proc(v1, v2):
            '''process 2 values assert they are of the same type'''
            #print 'proc>', v1, v2
            if   isinstance(v1, dict):
                procdict(v1, v2)
            elif isinstance(v1, list):
                proclist(v1, v2)
            else:
                if allow_none and v2 is None: return
                type_ = gettype(v1)
                try: assert isinstance(v2, type_)
                except: raise AssertionError, "%s must be of type %s, got type %s" % (v2, type_, str(type(v2)))
        def proclist(t, d):
            '''process a list type'''
            assert len(t) == 1
            if not isinstance(d, list):
                raise AssertionError, "Expected a <type 'list'> got %s" % type(d)
            v1 = t[0]
            for v2 in d:
                #print v1, v2
                proc(v1, v2)
        def procdict(t, d):
            '''process a dictionary type'''
            if not isinstance(d, dict):
                raise AssertionError, "Expected a <type 'dict'> got %s, '%s'" \
                    % (type(d), str(d))
            tkeys = set(t.keys());
            dkeys = set(d.keys());
            if '__undefinedkeys__' in tkeys:
                v1 = t['__undefinedkeys__']
                for v2 in d.values():
                    proc(v1, v2)
            else:
                for k in dkeys:
                    try: assert k in tkeys
                    except:
                        raise AssertionError, \
                            "%s must be in %s" % (k, str(tkeys))
                for k in tkeys:
                    try: assert k in dkeys
                    except:
                        raise AssertionError, \
                            "Missing key '%s' in %s" % (k, str(d))
                for k in dkeys:
                    #print '> ', k
                    v1 = t[k]
                    v2 = d[k]
                    proc(v1, v2)
        procdict(self.schema, d)

