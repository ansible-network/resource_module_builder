# Copyright (c) 2019 Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type  # pylint: disable=C0103

import json
import re

from ansible.module_utils.six import iteritems
from ansible.utils.display import Display
from ansible.errors import AnsibleFilterError
from ansible.utils.unsafe_proxy import AnsibleUnsafeText
from ansible.parsing.yaml.objects import AnsibleUnicode
from collections import OrderedDict

OPTIONS_METADATA = ('type', 'elements', 'default', 'choices', 'required')
SUBOPTIONS_METADATA = ('mutually_exclusive', 'required_together',
                       'required_one_of', 'supports_check_mode', 'required_if')
SENSITIVE_KEYS = ["key_exchange", "key_value", "ntp_key", "passphrase", "password", "secret"]

display = Display()

def convert_to_plain_python(obj):
    """
    Recursively convert Ansible internal types and OrderedDict to plain Python types.
    """
    if isinstance(obj, AnsibleUnsafeText) or isinstance(obj, AnsibleUnicode):
        return str(obj)
    elif isinstance(obj, dict) or isinstance(obj, OrderedDict):
        # Only call .items() for dictionary-like objects
        return {convert_to_plain_python(key): convert_to_plain_python(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        # Directly iterate over list elements
        return [convert_to_plain_python(element) for element in obj]
    else:
        return obj

def retrieve_metadata(values, out):
    for key in OPTIONS_METADATA:
        if key in values:
            data = values.get(key, None)
            if data:
                out[key] = data


def dive(obj, result):
    if isinstance(obj, dict):
        for k, val in iteritems(obj):
            if isinstance(val, dict):
                result[k] = {}
                retrieve_metadata(val, result[k])
                if k in SENSITIVE_KEYS:
                    result[k]['no_log'] = True
                suboptions = val.get('suboptions')
                if suboptions:
                    for item in SUBOPTIONS_METADATA:
                        if item in val:
                            result[k][item] = val[item]
                    result[k]['options'] = {}
                    dive(suboptions, result[k]['options'])
            elif isinstance(val, list):
                # Handle list elements
                result[k] = [dive(elem, {}) for elem in val if isinstance(elem, dict)]
            else:
                # Directly assign non-dict and non-list elements
                result[k] = val
    return result

def to_argspec(spec):
    if 'DOCUMENTATION' not in spec:
        raise AnsibleFilterError("missing required element 'DOCUMENTATION'"
                                 " in model")

    if not isinstance(spec['DOCUMENTATION'], dict):
        raise AnsibleFilterError("value of element 'DOCUMENTATION'"
                                 " should be of type dict")
    result = {}
    
    plain_value = convert_to_plain_python(spec['DOCUMENTATION'])
    dive(plain_value['options'], result)

    result = json.dumps(result, indent=1)
    result = re.sub(r'":\s*true', '": True', result)
    result = re.sub(r'":\s*false', '": False', result)
    display.debug("Arguments: %s" % result)
    return result


class FilterModule(object):
    def filters(self):
        return {
            'to_argspec': to_argspec,
        }
