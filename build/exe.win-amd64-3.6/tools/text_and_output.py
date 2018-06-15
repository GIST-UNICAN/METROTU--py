# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 17:07:26 2018

@author: Thorin
"""
from functools import wraps
from textwrap import fill
from logging import debug, info, error, warning


def pretty_output(*args, separator=" ",
                  width=80,  # fill.__defaults__[0],
                  fill=fill, map=map):
    separator_line = separator*width
    return fill("\n".join(("\n", separator_line,
                           *map(str, args),
                           separator_line, "\n")),
                width=width,
                drop_whitespace=False)


def prettier(func):
    @wraps(func)
    def prettier_logger(*args, **kwargs):
        func(pretty_output(*args, **kwargs))
    return prettier_logger


def enclose_with_quotes(t):
    return t.join(("'",)*2)


pretty_debug, pretty_info, pretty_error, pretty_warning = map(prettier,
                                                              (debug,
                                                               info,
                                                               error,
                                                               warning))


def pretty_print(*args, **kwargs):
    print(pretty_output(*args, **kwargs))
