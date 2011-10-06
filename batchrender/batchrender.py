#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2011, PediaPress GmbH
# See README.txt for additional licensing information.

import subprocess
import os
import py
import time
from multiprocessing import Process
import shutil
import argparse
import urlparse


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
        self.zip_fn = self._get_path('.zip')
        self.fetch_log = self._get_path('_fetch.log')
        self.render_log = self._get_path('_render.log')

    def __str__(self):
        return '<{0}>'.format(self.collection_title)

    def _get_path(self, fn):
        return os.path.splitext(self.out_fn)[0] + fn

    def get_error_path(self, path):
        fn = os.path.basename(path)
        return os.path.join(config.error_dir, fn)

    def report_error(self, cmd):
        cmd_fn = self._get_path('.cmd')
        open(cmd_fn, 'w').write(' '.join(cmd))

        shutil.move(cmd_fn, self.get_error_path(cmd_fn))

        for path in [self.fetch_log, self.render_log]:
            if os.path.exists(path):
                shutil.move(path, self.get_error_path(path))


    def clean(self):
        for path in [self.zip_fn,
                     self.fetch_log,
                     self.render_log]:
            if os.path.exists(path):
                os.unlink(path)

class BatchRender(object):

    def __init__(self):
        pass

    @property
    def collections(self):
        return [Collection(*collection_info) for collection_info in config.collection_list]

    def run_cmd(self, cmd):
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        out, err = p.communicate()
        return err

    def fetch(self, collection):
        cmd = ['mw-zip',
               '-c', collection.config_url,
               '--collectionpage', collection.collection_title,
               '-l', collection.fetch_log,
               '-o', collection.zip_fn,
               '-x', # FIXME: noimages - speed up fetching while debugging
               ]
        err = self.run_cmd(cmd)
        if not os.path.exists(collection.zip_fn) or err:
            collection.report_error(cmd)
            raise Exception('ERROR while fetching')

    def render(self, collection):
        cmd = ['mw-render',
               '-w', config.writer,
               '-c', collection.zip_fn,
               '-o', collection.out_fn,
               '-l', collection.render_log,
            ]
        err = self.run_cmd(cmd)
        if not os.path.exists(collection.zip_fn) or err:
            collection.report_error(cmd)
            raise Exception('ERROR while fetching')


    def update_feed(self, collection):
        url = urlparse.urljoin(config.zim_base_url, os.path.basename(collection.out_fn))
        cmd = ['kiwix-manage',
               config.zim_feed_file,
               'add', collection.out_fn,
               url
               ]

        err = self.run_cmd(cmd)
        if err:
            collection.report_error(cmd)
            raise Exception('ERROR while updating zim feed data')

    def create_feed(self):
        for collection in self.collections:
            self.update_feed(collection)

    def run(self):
        fetch_queue = self.collections
        fetch_active = []

        render_queue = []
        render_active = []

        pid2col = {}

        while fetch_queue or fetch_active or render_queue or render_active:
            # FETCH
            for p in fetch_active:
                if not p.is_alive():
                    fetch_active.remove(p)
                    log('fetching finished:',
                        pid2col[p.pid],
                        '(', p.pid, 'exitcode', p.exitcode, ')')
                    if p.exitcode == 0:
                        render_queue.append(pid2col[p.pid])
            
            while len(fetch_active) < config.max_parallel_fetch and fetch_queue:
                collection = fetch_queue.pop()
                p = Process(target=self.fetch, args=(collection,))
                p.start()
                fetch_active.append(p)
                log('fetching started',
                    collection,
                    '(', p.pid, ')')
                pid2col[p.pid] = collection

            # RENDER

            for p in render_active:
                if not p.is_alive():
                    collection = pid2col[p.pid]
                    collection.clean()
                    render_active.remove(p)
                    log('rendering finished:',
                        collection,
                        '(', p.pid, 'exitcode', p.exitcode, ')')
                    if p.exitcode == 0 and config.generate_zim_feed and config.writer == 'zim':
                        self.update_feed(collection) # blocking call, but it should be fast
                        log('updated zim feed', collection)
                
            while len(render_active) < config.max_parallel_render and render_queue:
                collection = render_queue.pop()
                p = Process(target=self.render, args=(collection,))
                p.start()
                render_active.append(p)
                log('rendering started', collection.collection_title, '(', p.pid, ')' )
                pid2col[p.pid] = collection

            time.sleep(5)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--createfeed', action='store_true')
    args = parser.parse_args()

    br = BatchRender()

    if args.createfeed:
        br.create_feed()
    else:
        br.run()

if __name__ == '__main__':
    main()
