#!/usr/bin/env python3

from functools import partial, wraps
from collections import deque, namedtuple
from itertools import islice
from textwrap import fill
from contextlib import contextmanager
from logging import debug, info, error, warning
# from logging import debug


Headers_and_data = namedtuple("Headers_and_data",
                              ("headers", "data"))


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


def get_info_from_csv(csv_file,
                      Headers_and_data=Headers_and_data):

    from csv import reader as csv_reader

    reader = csv_reader(csv_file)
    iter_reader = iter(reader)
    headers = next(iter_reader)  # Drop the row with column names
    return Headers_and_data(headers, iter_reader)


def get_field_indexes(hyphens_row,
                      separator=" "):
    """
Takes the second text row from a rpt file, finds out the length of each field.
    """

    starting_index = 0
    for index, character in enumerate(hyphens_row):
        if(character == separator):
            yield (starting_index, index)
            starting_index = index + 1
    yield starting_index, len(hyphens_row)


def create_info_from_avl_file(rpt_file,
                              get_field_indexes=get_field_indexes,
                              Headers_and_data=Headers_and_data):
    rpt_iterator = iter(rpt_file)
    headers_row = next(rpt_iterator)
    hyphens_row = next(rpt_iterator)
    field_indexes = tuple(get_field_indexes(hyphens_row))

    def get_row_fields(row):
        return tuple(
            (row[slice(*index)].strip() for index in field_indexes))

    headers = get_row_fields(headers_row)
    row_generator = (get_row_fields(r) for r in rpt_iterator)
    return Headers_and_data(headers, row_generator)


@contextmanager
def info_getter_from_file_on_disk(file_path,
                                  getter,
                                  headers=True,
                                  encoding='utf-8-sig'):
    with open(file_path, encoding=encoding) as file:
        yield getter(file) if headers else next(islice(getter(file), 1, None))


info_getter_from_csv_file = partial(info_getter_from_file_on_disk,
                                    getter=get_info_from_csv)


info_getter_from_rpt_file = partial(info_getter_from_file_on_disk,
                                    getter=create_info_from_avl_file)

pretty_debug, pretty_info, pretty_error, pretty_warning = map(prettier,
                                                              (debug,
                                                               info,
                                                               error,
                                                               warning))
