# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
from ansible.parsing.yaml.dumper import AnsibleDumper
from ansible.errors import AnsibleFilterError
from ansible.module_utils.six import iteritems
import json
import jsonref
import yaml

__metaclass__ = type


def dive(obj, required=False):
    if not 'description' in obj:
        raise AnsibleFilterError('missing description key')
    result = {'description': obj['description']}
    if not 'type' in obj:
        raise AnsibleFilterError('missing type key')
    if obj['type'] == 'object':
        result['suboptions'] = {}
        if not 'properties' in obj:
            raise AnsibleFilterError('missing properties key')
        for propkey, propval in obj['properties'].iteritems():
            required = bool('required' in obj and propkey in obj['required'])
            result['suboptions'][propkey] = dive(propval, required)
    elif obj['type'] == 'array':
        result['suboptions'] = {}
        if not 'items' in obj:
            raise AnsibleFilterError('missing items key in array')
        if not 'properties' in obj['items']:
            raise AnsibleFilterError('missing properties in items')
        for propkey, propval in obj['items']['properties'].iteritems():
            required = bool('required' in obj['items'] and propkey in obj['items']['required'])
            result['suboptions'][propkey] = dive(propval, required)
    elif obj['type'] in ['str', 'bool', 'int']:
        if 'default' in obj:
            result['default'] = obj['default']
        if 'enum' in obj:
            result['choices'] = obj['enum']
        if 'version_added' in obj:
            result['version_added'] = obj['version_added']
        if required:
            result['required'] = required
        result['type'] = obj['type']
    return result

def to_docoptions(value):
    data = jsonref.loads(json.dumps(value))
    result = dive(data['schema'])
    dumper = AnsibleDumper
    dumper.ignore_aliases = lambda *args: True
    options = {'options': result['suboptions']}
    result = yaml.dump(options, Dumper=dumper, indent=2,
                       allow_unicode=True, default_flow_style=False)
    return result

class FilterModule(object):
    def filters(self):
        return {
            'to_docoptions': to_docoptions,
        }
