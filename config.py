#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2011, PediaPress GmbH
# See README.txt for additional licensing information.

import os

collection_list_location = 'collection_list'
#update_frequency =

output_basedir = os.path.expanduser('~/data/batchrender')

writer = 'rl'
file_ext = '.pdf'


def get_collection_list(fn):
    collection_list = []
    for line in open(fn).readlines():
        collection_info = line.strip().split('\t')
        #expected format:
        #config_url \t collection_title \t zim_file_name
        collection_list.append(collection_info)
    return collection_list
collection_list = get_collection_list(collection_list_location)
