#!/usr/bin/python
# encoding=UTF-8
# Copyright © 2008, 2009 Jakub Wilk <ubanus@users.sf.net>
#
# This package is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

def parse_page_numbers(pages):
    '''
    >>> parse_page_numbers(None)

    >>> parse_page_numbers('17')
    [17]

    >>> parse_page_numbers('37-42')
    [37, 38, 39, 40, 41, 42]

    >>> parse_page_numbers('17,37-42')
    [17, 37, 38, 39, 40, 41, 42]

    >>> parse_page_numbers('42-37')
    []

    >>> parse_page_numbers('17-17')
    [17]
    '''
    if pages is None:
        return
    result = []
    for page_range in pages.split(','):
        if '-' in page_range:
            x, y = map(int, page_range.split('-', 1))
            result += xrange(x, y + 1)
        else:
            result += int(page_range, 10),
    return result

# vim:ts=4 sw=4 et