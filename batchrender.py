#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2011, PediaPress GmbH
# See README.txt for additional licensing information.

import subprocess
import os

import config


class BatchRender(object):

    def __init__(self):
        pass

    def run_cmd(self, cmd):
        print 'cmd:', cmd
        res = subprocess.call(cmd)
        if not res:
            print 'zip finished'
        else:
            print 'error', res
        

    def fetch(self, config_url, collection_title, zip_fn):
        cmd = ['mw-zip',
               '-c', config_url,
               '--collectionpage', collection_title,
               '-o', zip_fn
               ]
        self.run_cmd(cmd)

    def render(self, zip_fn, zim_fn, writer):
        cmd = ['mw-render',
               '-w', writer,
               '-c', zip_fn,
               '-o', zim_fn,
            ]
        self.run_cmd(cmd)

    def run(self):
        for config_url, collection_title, out_fn in config.collection_list:
            print '*'*40
            out_fn = os.path.join(config.output_basedir, out_fn + config.file_ext)
            zip_fn = os.path.splitext(out_fn)[0] + '.zip'
            self.fetch(config_url, collection_title, zip_fn)
            self.render(zip_fn, out_fn, config.writer)

if __name__ == '__main__':
    br = BatchRender()
    br.run()
