# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
import jsonref
import json
import pprint
from ansible.module_utils.six import iteritems

__metaclass__ = type

from ansible.errors import AnsibleFilterError

def dive(obj, required=False):
    result = {}
    if not 'type' in obj:
        raise AnsibleFilterError('missing type key')
    if obj['type'] == 'object':
        result['options'] = {}
        if not 'properties' in obj:
            raise AnsibleFilterError('missing properties key')
        for propkey, propval in iteritems(obj['properties']):
            required = bool('required' in obj and propkey in obj['required'])
            result['options'][propkey] = dive(propval, required)
    elif obj['type'] == 'array':
        result['options'] = {}
        if obj['elements']:
            result['elements'] = obj['elements']
        if not 'items' in obj:
            raise AnsibleFilterError('missing items key in array')
        if not 'properties' in obj['items']:
            raise AnsibleFilterError('missing properties in items')
        for propkey, propval in iteritems(obj['items']['properties']):
            required = bool('required' in obj['items'] and propkey in obj['items']['required'])
            result['options'][propkey] = dive(propval, required)
            result['type'] = 'list'
    elif obj['type'] in ['str', 'bool', 'int']:
        if 'default' in obj:
            result['default'] = obj['default']
        if 'enum' in obj:
            result['choices'] = obj['enum']
        if 'version_added' in obj:
            result['version_added'] = obj['version_added']
        result['required'] = required
        result['type'] = obj['type']
    return result

def to_argspec(value):
    data = jsonref.loads(json.dumps(value))
    result = dive(data['schema'])
    return str(result['options'])


class FilterModule(object):
    def filters(self):
        return {
            'to_argspec': to_argspec,
        }
