# Copyright (c) 2019 Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import yaml
from ansible.utils.unsafe_proxy import AnsibleUnsafeText
from ansible.parsing.yaml.objects import AnsibleUnicode
from collections import OrderedDict
from ansible.utils.display import Display

display = Display()


class CustomDumper(yaml.SafeDumper):
    pass


def represent_ansible_unicode(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data))


def represent_ordered_dict(dumper, data):
    return dumper.represent_dict(data.items())


CustomDumper.add_representer(AnsibleUnsafeText, represent_ansible_unicode)
CustomDumper.add_representer(OrderedDict, represent_ordered_dict)


def convert_to_plain_python(obj):
    """
    Recursively convert Ansible internal types and OrderedDict to plain Python types.
    """
    if isinstance(obj, AnsibleUnsafeText) or isinstance(obj, AnsibleUnicode):
        return str(obj)
    elif isinstance(obj, dict) or isinstance(obj, OrderedDict):
        return {
            convert_to_plain_python(key): convert_to_plain_python(value)
            for key, value in obj.items()
        }
    elif isinstance(obj, list):
        return [convert_to_plain_python(element) for element in obj]
    else:
        return obj


def order_dict(obj, priority_keys):
    """
    Order dictionary keys with specified keys first, followed by others alphabetically.
    """
    if isinstance(obj, dict):
        # Create an ordered dictionary with prioritized keys
        ordered = OrderedDict((k, obj[k]) for k in priority_keys if k in obj)

        # Add the remaining keys in alphabetical order
        for key in sorted(obj.keys()):
            if key not in ordered:
                ordered[key] = obj[key]

        # Recursively apply ordering to nested dictionaries
        return OrderedDict(
            (k, order_dict(v, priority_keys)) for k, v in ordered.items()
        )
    elif isinstance(obj, list):
        return [order_dict(element, priority_keys) for element in obj]
    else:
        return obj


def to_doc(value):
    priority_keys = [
        "module",
        "short_description",
        "description",
        "type",
        "required",
        "elements",
        "choices",
        "suboptions",
    ]
    plain_value = convert_to_plain_python(value)
    ordered_value = order_dict(plain_value, priority_keys)
    result = yaml.dump(
        ordered_value,
        Dumper=CustomDumper,
        default_flow_style=False,
        width=140,
        indent=2,
        allow_unicode=True,
    )
    display.debug("Arguments: %s" % result)
    return result


class FilterModule(object):
    def filters(self):
        return {"to_doc": to_doc}
