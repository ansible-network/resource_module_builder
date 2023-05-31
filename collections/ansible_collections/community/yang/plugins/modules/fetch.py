#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2020 Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: fetch
short_description: Fetch given yang model and it's dependencies
author: Ganesh Nalawade (@ganeshrn)
description:
    - Fetch given yang model and its dependant yang model from device using netconf rpc.
options:
  name:
    description:
      - Name of the yang model to fetched from remote host. This will also fetch all
        the dependent yang models and return as part of result. If the value is set
        to I(all) in that case all the yang models supported by remote host will be
        fetched.
  dir:
    description:
      - This is an optional argument which provide the directory path in which the fetched
        yang modules will be saved. The name of the file is same as that of the yang module
        name prefixed with `.yang` extension.
  continue_on_failure:
    description:
      - This is an optional arguement that allows schema fetch to continue if one the
        desired models fails download
    type: bool
    default: false
requirements:
- ncclient (>=v0.5.2)
- pyang
- xmltodict
notes:
- This module requires the NETCONF system service be enabled on the remote device
  being managed.
- This module supports the use of connection=ansible.netcommon.netconf
- If no options provided it will return list of yang model name supported by remote host
"""
RETURN = """
number_schema_fetched:
  description: Total number of yang model fetched from remote host
  returned: always apart from low-level errors (such as action plugin)
  type: int
  sample: 10
fetched:
  description: This is a key-value pair were key is the name of the yang model and value
               is the yang model itself in string format
  returned: always apart from low-level errors (such as action plugin)
  type: dict
  sample: {"ietf-inet-types": "module ietf-inet-types ...<--snip-->"}
supported_yang_modules:
  description: List of supported yang models name
  returned: only when model name is not provided
  type: list
  sample: ["ietf-netconf-monitoring", "cisco-xr-ietf-netconf-monitoring-deviations"]
failed_yang_modules:
  description: List of yang models that failed download
  returned: only when continue_on_failure is true
  type: list
  sample: ["ietf-netconf-monitoring", "cisco-xr-ietf-netconf-monitoring-deviations"]
"""
EXAMPLES = """
- name: Fetch given yang model from remote host
  community.yang.fetch:
    name: "{{ item }}"
  loop:
    - openconfig-interface
    - openconfig-bgp

- name: Fetch list of supported yang model names
  community.yang.fetch:

- name: Fetch all the yang models supported by remote host and store it in dir location
  community.yang.fetch:
    name: all
    dir: "{{ playbook_dir }}/yang_files"

- name: Fetch all the yang models supported by remote host and store it in dir location do not stop on error
  community.yang.fetch:
    name: all
    dir: "{{ playbook_dir }}/yang_files"
    continue_on_failure: true
"""
