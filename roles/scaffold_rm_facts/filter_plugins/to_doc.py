# Copyright (c) 2019 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import shutil
from subprocess import Popen, PIPE

from copy import deepcopy

from ansible.module_utils.six import StringIO, string_types
from ansible.errors import AnsibleError, AnsibleFilterError
from ansible.utils.display import Display
from ansible.utils.path import unfrackpath, makedirs_safe

display = Display()

SECTIONS = ('ANSIBLE_METADATA', 'DOCUMENTATION', 'EXAMPLES', 'RETURN')

DOC_SECTION_SANITIZE = ('mutually_exclusive', 'required_together',
                        'required_one_of', 'supports_check_mode',
                        'required_if')

DEFAULT_RETURN = """
before:
  description: The configuration prior to the model invocation.
  returned: always
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
after:
  description: The resulting configuration model invocation.
  returned: when changed
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
  sample: ['command 1', 'command 2', 'command 3']
"""

output = StringIO()
RM_DIR_PATH = "~/.ansible/tmp/resource_model"


def to_list(val):
    if isinstance(val, (list, tuple, set)):
        return list(val)
    elif val is not None:
        return [val]
    return list()


def add(line, spaces=0, newline=True):
    line = line.rjust(len(line)+spaces, ' ')
    if newline:
        output.write(line + '\n')
    else:
        output.write(line)


def get_ansible_metadata(spec, _path):
    # write ansible metadata
    if 'ANSIBLE_METADATA' not in spec:
        raise AnsibleFilterError("missing required element 'ANSIBLE_METADATA'"
                                 " in model")

    metadata = spec['ANSIBLE_METADATA']
    if not isinstance(metadata, string_types):
        raise AnsibleFilterError("value of element 'ANSIBLE_METADATA'"
                                 " should be of type string")

    add('ANSIBLE_METADATA = %s' % metadata, newline=True)
    # add(metadata)


def get_documentation(spec, _path):
    # write documentation
    if 'DOCUMENTATION' not in spec:
        raise AnsibleFilterError("missing required element 'DOCUMENTATION'"
                                 " in model")

    doc = spec['DOCUMENTATION']
    if not isinstance(doc, string_types):
        raise AnsibleFilterError("value of element 'DOCUMENTATION' should be"
                                 " of type string")

    add('DOCUMENTATION = """')
    add('---')
    add('%s' % doc)
    add('"""')


def get_examples(spec, path):
    # write examples
    if 'EXAMPLES' not in spec:
        raise AnsibleFilterError("missing required element 'EXAMPLES'"
                                 " in model")

    add('EXAMPLES = """')
    dir_name = os.path.dirname(path)
    for item in to_list(spec['EXAMPLES']):
        with open(os.path.join(dir_name, item)) as fileh:
            add(fileh.read().strip("\n"))
        add("\n")
    add('"""')


def get_return(spec, _path):
    # write return
    ret = spec.get('RETURN')
    add('RETURN = """')
    if ret:
        add(ret)
    else:
        add(DEFAULT_RETURN.strip())
    add('"""')


def validate_model(model, contents):
    try:
        resource_module_dir = unfrackpath(RM_DIR_PATH)
        makedirs_safe(resource_module_dir)
        module_name = "%s_%s" % (model['NETWORK_OS'], model['RESOURCE'])
        module_file_path = os.path.join(RM_DIR_PATH, '%s.%s' % (module_name,
                                                                'py'))
        exxpath = os.path.expanduser(module_file_path)
        module_file_path = os.path.realpath(exxpath)
        with open(module_file_path, 'w+') as fileh:
            fileh.write(contents)

        display.debug("Module file: %s" % module_file_path)

        # validate the model
        cmd = ["ansible-doc", "-M", os.path.dirname(module_file_path),
               module_name]
        proco = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = proco.communicate()
        if err:
            raise AnsibleError("Error while parsing module: %s" % err)
        display.debug("Module output:\n%s" % out)
    except Exception as err:
        raise AnsibleError('Failed to validate the model with error: %s\n%s'
                           % (err, contents))
    finally:
        expuser = os.path.expanduser(resource_module_dir)
        shutil.rmtree(os.path.realpath(expuser), ignore_errors=True)


def _sanitize_documentation(doc):
    sanitize_doc = []
    for line in doc.splitlines():
        for item in DOC_SECTION_SANITIZE:
            if line.strip().startswith(item):
                break
        else:
            sanitize_doc.append(line)
    return "\n".join(sanitize_doc)


def to_doc(rm, path):
    model = deepcopy(rm)
    model['DOCUMENTATION'] = _sanitize_documentation(rm['DOCUMENTATION'])
    path = os.path.realpath(os.path.expanduser(path))
    if not os.path.isfile(path):
        raise AnsibleFilterError("model file %s does not exist" % path)

    for name in SECTIONS:
        func = globals().get('get_%s' % name.lower())
        func(model, path)

    contents = output.getvalue()
    display.debug("%s" % contents)
    validate_model(model, contents)

    return contents


class FilterModule(object):
    def filters(self):
        return {
            'to_doc': to_doc,
        }
