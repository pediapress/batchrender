#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2011, PediaPress GmbH
# See README.txt for additional licensing information.

import os
import py

log = py.log.Producer('config')

class Config(object):

    def __init__(self):
        self.collection_list_location = os.path.expanduser('~/batchrender_collections')
        self.output_basedir = os.path.expanduser('~/')
        self.error_dir = os.path.expanduser('~/')
        self.writer = 'rl'
        self.max_parallel_fetch = 1
        self.max_parallel_render = 1
        self.generate_zim_feed = True
        self.zim_feed_file = ''
        self.zim_base_url = ''

        self.readrc()
        self.collection_list = self.get_collection_list(self.collection_list_location)
        self.file_ext = self.get_output_extension()
        self.make_dirs()

    def make_dirs(self):
        for path in [self.output_basedir, self.error_dir]:
            if not os.path.exists(path):
                os.makedirs(path)

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
                if getattr(self, attr).__class__ == int:
                    cast = lambda x: int(x)
                elif getattr(self, attr).__class__ ==  bool:
                    cast = lambda x: True if x in ['True', '1'] else False
                else:
                    cast = lambda x:x
                setattr(self, attr, cast(val))

    def get_collection_list(self, fn):
        collection_list = []
        for line in open(fn).readlines():
            if line.startswith('#'):
                continue
            collection_info = line.strip().split('\t')
            if len(collection_info) != 3:
                log('ERROR: collection info invalid:', collection_info)
                continue
            collection_list.append(collection_info)
        return collection_list

    def get_output_extension(self):
        ext_map = {'rl':'.pdf',
               'zim':'.zim'
            }
        assert self.writer in ext_map, 'ERROR: Invalid Writer'
        return ext_map[self.writer]





