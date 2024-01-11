"""Ansible Resource Module Builder output plugin
Generates a YML that presents resource module skeleton
of the YANG module.
"""

import logging
from pyang import plugin, error
import re


def pyang_plugin_init():
    plugin.register_plugin(AnsibleOldPlugin())


def order_dict(d, ordered_keys):
    new_dict = {}
    for key in ordered_keys:
        if key in d:
            value = d[key]
            if isinstance(value, dict):
                value = order_dict(value, ordered_keys)
            new_dict[key] = value
    for key in d:
        if key not in ordered_keys:
            value = d[key]
            if isinstance(value, dict):
                value = order_dict(value, ordered_keys)
            new_dict[key] = value
    return new_dict


class AnsibleOldPlugin(plugin.PyangPlugin):
    def __init__(self):
        super().__init__("ansible_old")
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
                    logging.error("Methodology: Custom enumeration type found. Using handle_custom_enum.")
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

        if yang_type == "identityref":
            logging.error(f"({key_count}) identityref type found. Using `handle_identity`.")
            ansible_type = self.handle_identity(type_node, child)
            logging.error(f"determined: {ansible_type}")
            return {"type": "str", "choices": ansible_type}

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

    def handle_identity(self, type_node, child):
        logging.error(f"Handling identityref for {child.arg}")
        identity_list = self.get_identity_list(type_node, child)
        logging.error(f"Identity list for {child.arg}: {identity_list}")
        return identity_list

    def get_identity_list(self, type_node, child):
        # Get the type specification of the identityref
        type_spec = type_node.i_type_spec

        if not hasattr(type_spec, 'base'):
            logging.error(f"No base identity found for {child.arg}")
            return []

        base_identity = type_spec.base
        if not base_identity:
            logging.error(f"Base identity for {child.arg} is None")
            return []

        # Collect all identities derived from the base identity
        identities = self.collect_derived_identities(base_identity)

        # Extract the names of the identities
        identity_names = [identity.arg for identity in identities]

        return identity_names

    def collect_derived_identities(self, base_identity):
        derived_identities = []

        # Check if base_identity is not None
        if base_identity and hasattr(base_identity, 'i_module') and base_identity.i_module:
            for identity in base_identity.i_module.i_identities.values():
                if self.is_derived_identity(identity, base_identity):
                    derived_identities.append(identity)

        return derived_identities
    def is_derived_identity(self, identity, base_identity):
        while identity:
            if identity == base_identity:
                return True
            identity = identity.base
        return False

    def process_module(self, module, path, fd):
        global key_count  # Declare counter as global to read
        logging.critical(f"Starting processing for module {module.arg}. Total keys processed so far: {key_count}.")
        data = self.yang_to_dict(module, path)
        ordered_data = order_dict(data, ["description", "type", "elements", "choices", "suboptions"])
        yaml_data = ez_yaml.to_string(ordered_data, settings = dict(width=130))
        fd.write(yaml_data)

    def preprocess_string(self, s):
        result = re.sub(r'\s+', ' ', s)
        return result.replace(':', ';')

    def yang_to_dict(self, yang_module, path):
        data = {}
        for child in yang_module.i_children:
            logging.warning(child)
            status_node = child.search_one("status")
            if status_node and status_node.arg == "deprecated":
                logging.warning(f"Skipping deprecated leaf: {child.arg}")
                continue  # Skip this leaf but continue processing siblings
            key_name = child.arg.replace("-", "_")
            if child.keyword in ["leaf", "leaf-list"]:
                if child.i_config:
                    ansible_type = self.yang_type_to_ansible_type(child)
                    mandatory_field = child.search_one("mandatory")
                    is_mandatory = mandatory_field.arg == "true" if mandatory_field else False

                    data[key_name] = {
                        "type": ansible_type if type(ansible_type) is str else ansible_type["type"],
                        "description": self.preprocess_string(child.search_one("description").arg)
                        if child.search_one("description")
                        else "",
                        "required": is_mandatory,
                    }
                    if type(ansible_type) is dict:
                        for key, value in ansible_type.items():
                            if key != "type":
                                data[key_name][key] = value

            elif child.keyword in ["container", "list"]:
                if child.i_config:
                    suboptions = self.yang_to_dict(child, path)
                    is_dict_elements = any(sub_child.keyword in ["container", "list"] for sub_child in child.i_children)
                    data[key_name] = {
                        "type": "list" if child.keyword == "list" else "dict",
                        "suboptions": suboptions,
                        "description": self.preprocess_string(child.search_one("description").arg)
                        if child.search_one("description")
                        else "",
                    }
                    if child.keyword == "list" and is_dict_elements:
                        data[key_name]["elements"] = "dict"
                    if child.keyword == "list" and not is_dict_elements:
                        data[key_name]["elements"] = "dict"
            elif child.keyword == "choice":
                if child.i_config:
                    data[key_name] = {
                        "type": "str",
                        "description": self.preprocess_string(child.search_one("description").arg)
                        if child.search_one("description")
                        else "",
                        "choices": [case.arg for case in child.i_children],
                    }

        return data
