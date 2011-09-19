#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2011, PediaPress GmbH
# See README.txt for additional licensing information.

import subprocess
import os
import py
import time
from multiprocessing import Process


from config import Config

config = Config()

log = py.log.Producer('batchrender')

class Collection(object):

    def __init__(self,
                 config_url,
                 collection_title,
                 out_fn):
        self.config_url = config_url.strip()
        self.collection_title = collection_title.strip()
        self.out_fn = os.path.join(config.output_basedir, out_fn.strip() + config.file_ext)
        self.zip_fn = os.path.splitext(self.out_fn)[0] + '.zip'
        self.fetch_log = os.path.splitext(self.out_fn)[0] + '_fetch.log'
        self.render_log = os.path.splitext(self.out_fn)[0] + '_render.log'

class BatchRender(object):

    def __init__(self):
        pass

    def run_cmd(self, cmd):
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        out, err = p.communicate()
        if err:
            log('ERROR command exited with error', err, cmd)
            raise Exception


    def fetch(self, collection):
        cmd = ['mw-zip',
               '-c', collection.config_url,
               '--collectionpage', collection.collection_title,
               '-l', collection.fetch_log,
               '-o', collection.zip_fn,
               '-x', # FIXME: noimages - speed up fetching while debugging
               ]
        self.run_cmd(cmd)
        assert os.path.exists(collection.zip_fn), 'ERROR: no zip file after fetching'

    def render(self, collection):
        cmd = ['mw-render',
               '-w', config.writer,
               '-c', collection.zip_fn,
               '-o', collection.out_fn,
               '-l', collection.render_log,
            ]
        self.run_cmd(cmd)
        assert os.path.exists(collection.out_fn), 'ERROR: no output file after rendering'

    def run(self):
        fetch_queue = [Collection(*collection_info) for collection_info in config.collection_list if not collection_info[0].startswith('#')]
        fetch_active = []

        render_queue = []
        render_active = []

        pid2col = {}

        while fetch_queue or fetch_active or render_queue or render_active:
            # FETCH
            for p in fetch_active:
                if not p.is_alive():
                    fetch_active.remove(p)
                    log('fetching finished:', pid2col[p.pid].collection_title,'(', p.pid, 'exitcode', p.exitcode, ')')
                    render_queue.append(pid2col[p.pid])
            
            while len(fetch_active) < config.max_parallel_fetch and fetch_queue:
                collection = fetch_queue.pop()
                p = Process(target=self.fetch, args=(collection,))
                p.start()
                fetch_active.append(p)
                log('fetching started', collection.collection_title, '(', p.pid, ')')
                pid2col[p.pid] = collection

            # RENDER

            for p in render_active:
                if not p.is_alive():
                    render_active.remove(p)
                    log('rendering finished:', pid2col[p.pid].collection_title,'(', p.pid, 'exitcode', p.exitcode, ')')
                
            while len(render_active) < config.max_parallel_render and render_queue:
                collection = render_queue.pop()
                p = Process(target=self.render, args=(collection,))
                p.start()
                render_active.append(p)
                log('rendering started', collection.collection_title, '(', p.pid, ')' )
                pid2col[p.pid] = collection

            time.sleep(5)
            

if __name__ == '__main__':
    br = BatchRender()
    br.run()
