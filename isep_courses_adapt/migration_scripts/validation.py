# -*- coding: utf-8 -*-
from datetime import date
import re


def create_name(firts, last):
    if firts is None:
        return last
    elif last is None:
        return firts
    else:
        if firts is None and last is None:
            return ''
        else:
            return firts + last


def cupr_or_dni(curp, dni):
    if curp is None:
        return dni
    elif dni is None:
        return curp
    else:
        return ''


def verify_id(id):
    if type(id) is tuple:
        if type(id[0]) is int:
            return id[0]
        else:
            return 'NULL'
    elif type(id) is int:
        return id
    else:
        return 'NULL'


def verify_char_field(field):
    if field is not None:
        return field
    else:
        return ''


def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).
    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))


def replace_special_caracter(args):
    s = re.split("'", args)
    args = ''
    for i in s:
        args = args + i
    return args