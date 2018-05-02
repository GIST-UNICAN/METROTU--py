# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 17:13:43 2018

@author: Juan
"""
from contextlib import contextmanager
from collections import namedtuple
from itertools import islice
from functools import partial

Headers_and_data = namedtuple("Headers_and_data",
                              ("headers", "data"))


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
