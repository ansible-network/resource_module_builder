import pprint
import yaml
import jsonref
import json


with open("models/myos/interfaces/myos_interfaces.yml", 'r') as stream:
    try:
        data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)


data = jsonref.loads(json.dumps(data))


#
# data = pluck(data)
#
# pprint(yaml.dump(data))
#
#
# yaml.Dumper.ignore_aliases = lambda *args : True
# print(yaml.dump(data, default_flow_style=False))
#


def dive(obj, required=False):
    # print('------------------------------')
    # print(obj)
    if not 'description' in obj:
        print('description missing in obj')
    result = {'description': obj['description']}
    if not 'type' in obj:
        print('type missing in obj')
    if obj['type'] == 'object':
        result['suboptions'] = {}
        if not 'properties' in obj:
            print('properties missing in obj')
        for propkey, propval in obj['properties'].items():
            required = bool('required' in obj and propkey in obj['required'])
            result['suboptions'][propkey] = dive(propval, required)
    elif obj['type'] == 'array':
        result['suboptions'] = {}
        if not 'items' in obj:
            print('items missing in obj')
        if not 'properties' in obj:
            print('items/properties missing in obj')
        for propkey, propval in obj['items']['properties'].items():
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

def u_to_str(object, context, maxlevels, level):
    typ = pprint._type(object)
    if typ is unicode:
        object = str(object)
    return pprint._safe_repr(object, context, maxlevels, level)


result = dive(data['schema'])
printer = pprint.PrettyPrinter()
printer.format = u_to_str
print(printer.pformat(result))
