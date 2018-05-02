# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 17:20:50 2018

@author: Juan
"""

from functools import wraps
from sys import exit as exit_progr


def make_exit_if_none(func, exit_progr=exit_progr):

    @wraps(func)
    def exits_if_none(*args, **kwargs):
        response = func(*args, **kwargs)
        return exit_progr() if response is None else response

    return exits_if_none
