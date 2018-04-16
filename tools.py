#!/usr/bin/env python3

from functools import partial
from collections import deque
from itertools import islice
from textwrap import fill
##from logging import debug

create_empty_deque = partial(deque, maxlen=0)

def exhaust_map(f, *i, create_empty_deque=create_empty_deque, map=map):
    """Allows us to pass arguments by batch to a function, ignoring the
    returned value, if any."""
    create_empty_deque(map(f, *i))

def create_object_factory(cl, *args, **kwargs):
    while True:
        yield cl(*args, **kwargs)

def create_objects(cl,
                   n,
                   islice=islice,
                   create_object_factory=create_object_factory,
                   *args,
                   **kwargs):
    return islice(create_object_factory(cl, *args, **kwargs), n)

def pretty_output(*args, separator=" ",
                  width=fill.__defaults__[0],
                  fill=fill, map=map):
    separator_line = separator*width
    return fill("\n".join((separator_line,
                           *map(str, args),
                           separator_line)),
                width=width,
                drop_whitespace=False)

def enclose_with_quotes(t):
    return t.join(("'",)*2)
