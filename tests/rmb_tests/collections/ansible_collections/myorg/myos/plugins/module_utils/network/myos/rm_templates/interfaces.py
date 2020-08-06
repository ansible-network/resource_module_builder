# -*- coding: utf-8 -*-
# Copyright 2020 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

"""
The Interfaces parser templates file. This contains 
a list of parser definitions and associated functions that 
facilitates both facts gathering and native command generation for 
the given network resource.
"""

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network_template import (
    NetworkTemplate,
)

class InterfacesTemplate(NetworkTemplate):
    def __init__(self, lines=None):
        super(InterfacesTemplate, self).__init__(lines=lines, tmplt=self)

    # fmt: off
    PARSERS = [
        {
            'name': 'resource',
            'getval': re.compile(r'''
              ^resource\s(?P<name>\S+)$''', re.VERBOSE),
            'setval': 'resource {{ name }}',
            'result': {
                '{{ name }}': {
                    'name': '{{ name }}'
                },
            },
            'shared': True
        },
        {
            'name': 'some_string',
            'getval': re.compile(r'''
              \s+a_string\s(?P<a_string>\S+)$''', re.VERBOSE),
            'setval': 'a_string {{ a_string }}',
            'result': {
                '{{ name }}': {
                    'some_string': '{{ a_string }}'
                },
            },
        },
        {
            'name': 'property_01',
            'getval': re.compile(r'''
              \s+key
              \sis
              \sproperty01
              \svalue
              \sis
              \s(?P<value>\S+)
              \send$''', re.VERBOSE),
            'setval': 'property_01 {{ value }}',
            'result': {
                '{{ name }}': {
                    'some_dict': {
                        'property_01': '{{ value }}'
                    }
                },
            },
        },
        {
            'name': 'some_bool',
            'getval': re.compile(r'''
              \s+(?P<some_bool>a_bool)$''', re.VERBOSE),
            'setval': 'some_bool',
            'result': {
                '{{ name }}': {
                    'some_bool': '{{ True if some_bool is defined else False }}'
                },
            },
        },
        {
            'name': 'some_int',
            'getval': re.compile(r'''
              \s+an_int\s(?P<some_int>\d+)$''', re.VERBOSE),
            'setval': 'some_int {{ some_int }}',
            'result': {
                '{{ name }}': {
                    'some_int': '{{ some_int }}'
                },
            },
        },
    ]
    # fmt: on
