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
    ]
    # fmt: on
