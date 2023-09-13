"""Ansible Resource Module Builder output plugin
Generates a YML that presents resource module skeleton
of the YANG module.
"""

import yaml
import logging
from pyang import plugin, error


def pyang_plugin_init():
    plugin.register_plugin(AnsiblePlugin())


class AnsiblePlugin(plugin.PyangPlugin):
    def __init__(self):
        super().__init__("ansible")
        global key_count  # Declare counter as global to modify
        key_count = 0  # Reset counter

    def get_type_node(self, child):
        logging.error(f"Getting type node for {child.arg}")
        type_node = child.search_one("type")
        if not type_node:
            logging.error(f"type_node is empty on {child.arg}")
            return None, "str"

        base_type_node = self.resolve_base_type(type_node)
        logging.error(f"Got base {base_type_node} {base_type_node.arg}")
        return base_type_node, base_type_node.arg

    def resolve_base_type(self, type_node):
        # Recursively resolve the base type
        while True:
            typedef = type_node.i_typedef
            if typedef is None:
                break
            type_node = typedef.search_one("type")
        return type_node

    def handle_enumeration(self, type_node):
        logging.error("Handling enumeration type")
        enums = [enum.arg for enum in type_node.search("enum")]
        return {"type": "str", "choices": enums}

    def handle_custom_enum(self, type_node):
        logging.error(f"Processing custom enum: {type_node}")
        enums = [enum.arg for enum in type_node.search("enum")]
        return {"type": "str", "choices": enums}

    def handle_custom_type(self, child, namespace, custom_type, root_module):
        logging.error(f"Handling custom type: {namespace}:{custom_type}")
        target_module = next((mod for mod in root_module.i_ctx.modules.values() if mod.i_prefix == namespace), None)
        if target_module:
            typedef_node = target_module.search_one("typedef", custom_type)
            if typedef_node:
                type_node = typedef_node.search_one("type")
                if type_node.arg == "enumeration":
                    logging.critical("Methodology: Custom enumeration type found. Using handle_custom_enum.")
                    return self.handle_custom_enum(type_node)
        else:
            typedef_node = None

        if typedef_node:
            logging.error("Typedef node found, proceeding.")
            type_node = typedef_node.search_one("type")
            if type_node:
                logging.error("Type node under typedef found.")
                return self.handle_string_custom_type(typedef_node)

    def handle_string_custom_type(self, typedef_node):
        logging.error("Handling custom string type")
        length_constraint = typedef_node.search_one("length")
        if length_constraint:
            logging.error(f"Length constraint found: {length_constraint.arg}")
            return {"type": "str", "max_length": int(length_constraint.arg.split("..")[1])}
        else:
            return {"type": "str"}

    def yang_type_to_ansible_type(self, child):
        global key_count  # Declare counter as global to modify
        key_count += 1  # Increment counter

        logging.critical(f"({key_count}) Determining type for key {child.arg}.")

        type_mapping = {
            "": "",
            "decimal64": "float",
            "string": "str",
            "int16": "int",
            "int32": "int",
            "uint8": "int",
            "uint16": "int",
            "uint32": "int",
            "boolean": "bool",
            "union": "str",
        }

        type_node, yang_type = self.get_type_node(child)
        key = child.arg
        if yang_type == "enumeration":
            logging.error(f"({key_count}) Enumeration type found. Using `handle_enumeration`.")
            ansible_type = self.handle_enumeration(type_node)
            logging.error(f"determined: {ansible_type}")
            return ansible_type

        if yang_type == "leafref":
            logging.error(f"({key_count}) leafref type found. Using `handle_leafref`.")
            ansible_type = self.handle_leafref(type_node, key)
            logging.error(f"determined: {ansible_type}")
            return ansible_type

        if ":" in yang_type:
            namespace, custom_type = yang_type.split(":")
            root_module = child.i_module
            while hasattr(root_module, "i_including_module"):
                root_module = root_module.i_including_module
            logging.error(f"Custom type found. Using `handle_custom_type`. for {namespace}:{custom_type}")
            ansible_type = self.handle_custom_type(child, namespace, custom_type, root_module)
            if ansible_type:
                logging.error(f"determined: {ansible_type}")
                return ansible_type

        if yang_type not in type_mapping:
            logging.error(f"Unhandled YANG type: {yang_type} on {key}")
            raise ValueError(f"Unhandled YANG type: {yang_type} on {key}")

        return type_mapping.get(yang_type, "str")

    def handle_leafref(self, type_node, key):
        """
        Handle leafref type by looking up the referenced type.
        """
        if hasattr(type_node, "i_leafref_ptr") and type_node.i_leafref_ptr:
            try:
                leafref_path = type_node.arg
                referenced_leaf = type_node.i_leafref_ptr
                if referenced_leaf is None:
                    logging.error(f"Could not find referenced leaf for leafref: {leafref_path}")
                    return "str"  # Defaulting to string type for unresolvable leafref

                # Retrieve the type of the referenced leaf
                referenced_type_node = referenced_leaf.search_one("type")
                referenced_type = referenced_type_node.arg

                # Your existing logic here to convert yang type to ansible type
                return self.yang_type_to_ansible_type(referenced_leaf)

            except AttributeError as e:
                logging.error(f"Error while handling leafref for key {key}: {e}")
                return "str"  # Defaulting to string type in case of an error
        else:
            logging.error(f"'TypeStatement' object has no attribute 'i_leafref_ptr'")
            return "str"  # or other fallback mechanism

    def add_output_format(self, fmts):
        self.multiple_modules = True
        fmts["ansible"] = self

    def emit(self, ctx, modules, fd):
        if ctx.opts.sample_path is not None:
            path = ctx.opts.sample_path.split("/")
            if path[0] == "":
                path = path[1:]
        else:
            path = []

        for module in modules:
            self.process_module(module, path, fd)

    def process_module(self, module, path, fd):
        global key_count  # Declare counter as global to read
        logging.critical(f"Starting processing for module {module.arg}. Total keys processed so far: {key_count}.")
        data = self.yang_to_dict(module, path)
        yaml_data = yaml.dump(data, default_flow_style=False)
        fd.write(yaml_data)

    def yang_to_dict(self, yang_module, path):
        data = {}
        for child in yang_module.i_children:
            status_node = child.search_one("status")
            if status_node and status_node.arg == "deprecated":
                logging.warning(f"Skipping deprecated leaf: {child.arg}")
                continue  # Skip this leaf but continue processing siblings
            key_name = child.arg.replace("-", "_")

            if child.keyword in ["leaf", "leaf-list"]:
                if child.i_config:
                    ansible_type = self.yang_type_to_ansible_type(child)
                    data[key_name] = {
                        "description": " ".join(child.search_one("description").arg.split("\n"))
                        if child.search_one("description")
                        else "",
                        "type": ansible_type if type(ansible_type) is str else ansible_type["type"],
                        "required": not bool(child.search_one("default")),
                    }
                    if type(ansible_type) is dict:
                        for key, value in ansible_type.items():
                            if key != "type":
                                data[key_name][key] = value

            elif child.keyword in ["container", "list"]:
                if child.i_config:
                    data[key_name] = {
                        "description": " ".join(child.search_one("description").arg.split("\n"))
                        if child.search_one("description")
                        else "",
                        "type": "list" if child.keyword == "list" else "dict",
                        "suboptions": self.yang_to_dict(child, path),
                    }

            elif child.keyword == "choice":
                if child.i_config:
                    data[key_name] = {
                        "description": " ".join(child.search_one("description").arg.split("\n"))
                        if child.search_one("description")
                        else "",
                        "type": "str",
                        "choices": [case.arg for case in child.i_children],
                    }

        return data
