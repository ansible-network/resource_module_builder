# Copyright (c) 2019 Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
from ansible.module_utils.six import StringIO
from ansible.errors import AnsibleFilterError
from ansible.utils.display import Display

display = Display()


def to_list(val):
    if isinstance(val, (list, tuple, set)):
        return list(val)
    elif val is not None:
        return [val]
    return list()


def get_examples(spec, path):
    output = StringIO()
    output.write('EXAMPLES = """\n')
    dir_name = os.path.dirname(path)
    for item in to_list(spec):
        with open(os.path.join(dir_name, item)) as fileh:
            output.write(fileh.read().strip("\n") + "\n")
    output.write('"""\n')
    return output.getvalue()


def to_examples(value, path):
    display.debug("value: %s" % value)
    display.debug("path: %s" % path)
    path = os.path.realpath(os.path.expanduser(path))
    if not os.path.isfile(path):
        raise AnsibleFilterError("model file %s does not exist" % path)

    result = get_examples(value, path)
    display.debug("Generated examples: %s" % result)
    return result


class FilterModule(object):
    def filters(self):
        return {"to_examples": to_examples}
