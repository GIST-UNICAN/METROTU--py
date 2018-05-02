# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 15:06:08 2018

@author: Juan
"""

from collections import namedtuple
from itertools import starmap


Name_and_pattern = namedtuple("Name_and_pattern", ("name", "pattern"))


all_files, xml, csv, rpt, dil = starmap(
        Name_and_pattern,
        (("All files", "*.*"),
         ("XML files", "*.xml"),
         ("Comma separated values files", "*.csv"),
         ("SQL report files", "*.rpt"),
         ("Dill dump files", "*.dil")))
