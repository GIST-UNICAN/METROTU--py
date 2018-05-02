#!/usr/bin/env python3

from functools import partial
from collections import deque
from itertools import islice, repeat

# from logging import debug


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


def create_instances(cl, n):
    return (c() for c in repeat(cl, n))


def get_defaults_adder(**kwargs):
    return partial(partial, **kwargs)
