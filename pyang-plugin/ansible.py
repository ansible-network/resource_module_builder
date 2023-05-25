"""Ansible Resource Module Builder output plugin
Generates a YML that presents resource module skeleton
of the YANG module.
"""

import yaml

from pyang import plugin, error


def pyang_plugin_init():
    plugin.register_plugin(AnsiblePlugin())


class AnsiblePlugin(plugin.PyangPlugin):
    def __init__(self):
        plugin.PyangPlugin.__init__(self, "ansible")

    def add_output_format(self, fmts):
        self.multiple_modules = True
        fmts["ansible"] = self

    def emit(self, ctx, modules, fd):
        if ctx.opts.sample_path is not None:
            path = ctx.opts.sample_path.split('/')
            if path[0] == '':
                path = path[1:]
        else:
            path = []

        for module in modules:
            self.process_module(module, path, fd)

    def process_module(self, module, path, fd):
        data = self.yang_to_dict(module, path)
        yaml_data = yaml.dump(data, default_flow_style=False)
        fd.write(yaml_data)

    def yang_to_dict(self, yang_module, path):
        data = {}
        for child in yang_module.i_children:
            if child.keyword in ["leaf", "leaf-list"]:
                data[child.arg] = {
                    'description': ' '.join(child.search_one('description').arg.split('\n')) if child.search_one('description') else '',
                    "type": child.search_one("type").arg if child.search_one("type") else "",
                    "required": not bool(child.search_one("default")),
                }
            elif child.keyword in ["container", "list"]:
                data[child.arg] = {
                    'description': ' '.join(child.search_one('description').arg.split('\n')) if child.search_one('description') else '',
                    "type": "list" if child.keyword == "list" else "dict",
                    "suboptions": self.yang_to_dict(child, path),
                }
            elif child.keyword == 'choice':
                data[child.arg] = {
                    'description': ' '.join(child.search_one('description').arg.split('\n')) if child.search_one('description') else '',
                    'type': 'str',
                    'choices': [case.arg for case in child.i_children],
                }
        return data
