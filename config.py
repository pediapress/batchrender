#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2011, PediaPress GmbH
# See README.txt for additional licensing information.

import os
import py

log = py.log.Producer('config')

class Config(object):

    def __init__(self):
        self.collection_list_location = os.path.expanduser('batchrender_collections')
        self.output_basedir = os.path.expanduser('~/')
        self.writer = 'rl'
        self.max_parallel_fetch = 1
        self.max_parallel_render = 1

        self.readrc()
        self.collection_list = self.get_collection_list(self.collection_list_location)
        self.file_ext = self.get_output_extension()
        assert os.path.exists(self.output_basedir), 'ERROR: output directory does not exist: %s' % self.output_basedir

    def readrc(self, path=None):
        if path is None:
            path = os.path.expanduser("~/.batchrender")
            if not os.path.exists(path):
                return
        cfg = py.iniconfig.IniConfig(path, None)
        if not cfg:
            return
        log('using config from', path)
        for attr, val in cfg['main'].items():
            if hasattr(self, attr):
                log('setting : %s=%s' % (attr, val))
                if isinstance(getattr(self, attr), int):
                    cast = lambda x: int(x)
                else:
                    cast = lambda x:x

                setattr(self, attr, cast(val))

    def get_collection_list(self, fn):
        collection_list = []
        for line in open(fn).readlines():
            collection_info = line.strip().split('\t')
            collection_list.append(collection_info)
        return collection_list

    def get_output_extension(self):
        ext_map = {'rl':'.pdf',
               'zim':'.zim'
            }
        assert self.writer in ext_map, 'ERROR: Invalid Writer'
        return ext_map[self.writer]





