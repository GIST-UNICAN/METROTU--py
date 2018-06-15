# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 17:18:45 2018

@author: Juan
"""

from dill import dump as dill_dump, load as dill_load


def save_dill_to_file_on_disk(path,
                              dill_dump=dill_dump,
                              **kwargs):
    with open(path, 'wb') as file:
        dill_dump(kwargs, file)


def load_dill_from_file_on_disk(path,
                                dill_load=dill_load):
    with open(path, 'rb') as file:
        dill_load(file)
