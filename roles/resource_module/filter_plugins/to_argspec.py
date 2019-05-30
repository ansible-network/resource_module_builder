# Copyright (c) 2019 Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type  # pylint: disable=C0103

import pprint
import yaml

from ansible.module_utils.six import iteritems
from ansible.module_utils.six import string_types
from ansible.utils.display import Display
from ansible.errors import AnsibleFilterError

OPTIONS_METADATA = ('type', 'elements', 'default', 'choices', 'required')
SUBOPTIONS_METADATA = ('mutually_exclusive', 'required_together',
                       'required_one_of', 'supports_check_mode', 'required_if')

display = Display()


def retrieve_metadata(values, out):
    for key in OPTIONS_METADATA:
        if key in values:
            data = values.get(key, None)
            if data:
                out[key] = data


def dive(obj, result):
    for k, val in iteritems(obj):
        result[k] = dict()
        retrieve_metadata(val, result[k])
        suboptions = val.get('suboptions')
        if suboptions:
            for item in SUBOPTIONS_METADATA:
                if item in val:
                    result[k][item] = val[item]
            result[k]['options'] = dict()
            dive(suboptions, result[k]['options'])

def to_argspec(spec):
    if 'DOCUMENTATION' not in spec:
        raise AnsibleFilterError("missing required element 'DOCUMENTATION'"
                                 " in model")

    if not isinstance(spec['DOCUMENTATION'], string_types):
        raise AnsibleFilterError("value of element 'DOCUMENTATION'"
                                 " should be of type string")
    result = {}
    doc = yaml.safe_load(spec['DOCUMENTATION'])

    dive(doc['options'], result)

    result = pprint.pformat(result, indent=1)
    display.debug("Arguments: %s" % result)
    return result


class FilterModule(object):
    def filters(self):
        return {
            'to_argspec': to_argspec,
        }
