# Copyright (c) 2019 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
from ansible.module_utils.six import StringIO
from ansible.errors import AnsibleFilterError
from ansible.utils.display import Display


display = Display()
output = StringIO()
RM_DIR_PATH = "~/.ansible/tmp/resource_model"


def add(line, spaces=0, newline=True):
    line = line.rjust(len(line) + spaces, " ")
    if newline:
        output.write(line + "\n")
    else:
        output.write(line)


def to_list(val):
    if isinstance(val, (list, tuple, set)):
        return list(val)
    elif val is not None:
        return [val]
    return list()


def get_examples(spec, path):
    # write examples

    add('EXAMPLES = """')
    dir_name = os.path.dirname(path)
    for item in to_list(spec):
        with open(os.path.join(dir_name, item)) as fileh:
            add(fileh.read().strip("\n"))
        add("\n")
    add('"""')

def to_examples(value, path):
    display.debug("value: %s" % value)
    display.debug("path: %s" % path)
    path = os.path.realpath(os.path.expanduser(path))
    if not os.path.isfile(path):
        raise AnsibleFilterError("model file %s does not exist" % path)

    result = get_examples(value, path)
    display.debug("%s" % result)
    return result


class FilterModule(object):
    def filters(self):
        return {"to_examples": to_examples}
