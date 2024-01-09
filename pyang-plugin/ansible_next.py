"""Foo output plugin
"""

# pylint: disable=C0111

from __future__ import print_function

import re
import ez_yaml
import optparse
import logging

from pyang import plugin
from pyang import statements
from pyang import types
from pyang import error


def pyang_plugin_init():
    plugin.register_plugin(FooPlugin())


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


class FooPlugin(plugin.PyangPlugin):
    def add_output_format(self, fmts):
        fmts["foo"] = self

    def add_opts(self, optparser):
        optlist = [
            optparse.make_option(
                "--foo-debug",
                dest="foo_debug",
                action="store_true",
                help="foo debug",
            ),
        ]

        group = optparser.add_option_group("foo-specific options")
        group.add_options(optlist)

    def setup_ctx(self, ctx):
        ctx.opts.stmts = None

    def setup_fmt(self, ctx):
        ctx.implicit_errors = False

    def emit(self, ctx, modules, fd):
        root_stmt = modules[0]
        if ctx.opts.foo_debug:
            logging.basicConfig(level=logging.DEBUG)
            print("")

        schema = produce_schema(root_stmt)

        ordered_data = order_dict(
            schema, ["description", "type", "elements", "choices", "suboptions"]
        )
        yaml_data = ez_yaml.to_string(ordered_data, settings=dict(width=130))
        fd.write(yaml_data)


def preprocess_string(s):
    result = re.sub(r"\s+", " ", s)
    return result.replace(":", ";")


def find_stmt_by_path(module, path):
    logging.debug(
        "in find_stmt_by_path with: %s %s path: %s", module.keyword, module.arg, path
    )

    if path is not None:
        spath = path.split("/")
        if spath[0] == "":
            spath = spath[1:]

    children = [
        child
        for child in module.i_children
        if child.keyword in statements.data_definition_keywords
    ]

    while spath is not None and len(spath) > 0:
        match = [
            child
            for child in children
            if child.arg == spath[0]
            and child.keyword in statements.data_definition_keywords
        ]
        if len(match) > 0:
            logging.debug("Match on: %s, path: %s", match[0].arg, spath)
            spath = spath[1:]
            children = match[0].i_children
            logging.debug("Path is now: %s", spath)
        else:
            logging.debug("Miss at %s, path: %s", children, spath)
            raise error.EmitError("Path '%s' does not exist in module" % path)

    logging.debug("Ended up with %s %s", match[0].keyword, match[0].arg)
    return match[0]


def produce_schema(root_stmt):
    logging.debug("in produce_schema: %s %s", root_stmt.keyword, root_stmt.arg)
    result = {}

    for child in root_stmt.i_children:
        if child.keyword in statements.data_definition_keywords:
            if child.keyword in producers:
                logging.debug("keyword hit on: %s %s", child.keyword, child.arg)
                add = producers[child.keyword](child)
                result.update(add)
            else:
                logging.debug("keyword miss on: %s %s", child.keyword, child.arg)
        else:
            logging.debug(
                "keyword not in data_definition_keywords: %s %s",
                child.keyword,
                child.arg,
            )
    return result


def produce_type(type_stmt):
    logging.debug("In produce_type with: %s %s", type_stmt.keyword, type_stmt.arg)
    type_id = type_stmt.arg

    if types.is_base_type(type_id):
        if type_id in _numeric_type_trans_tbl:
            type_str = numeric_type_trans(type_id)
        elif type_id in _other_type_trans_tbl:
            type_str = other_type_trans(type_id, type_stmt)
        else:
            logging.debug(
                "Missing mapping of base type: %s %s", type_stmt.keyword, type_stmt.arg
            )
            type_str = {"type": "string"}
    elif hasattr(type_stmt, "i_typedef") and type_stmt.i_typedef is not None:
        logging.debug(
            "Found typedef type in: %s %s (typedef) %s",
            type_stmt.keyword,
            type_stmt.arg,
            type_stmt.i_typedef,
        )
        typedef_type_stmt = type_stmt.i_typedef.search_one("type")
        typedef_type = produce_type(typedef_type_stmt)
        type_str = typedef_type
    else:
        logging.debug(
            "Missing mapping of: %s %s",
            type_stmt.keyword,
            type_stmt.arg,
            type_stmt.i_typedef,
        )
        type_str = {"type": "string"}
    return type_str


def produce_leaf(stmt):
    logging.debug("in produce_leaf: %s %s", stmt.keyword, stmt.arg)
    arg = qualify_name(stmt)

    type_stmt = stmt.search_one("type")
    type_str = produce_type(type_stmt)

    return {arg: type_str}


def produce_list(stmt):
    logging.debug("in produce_list: %s %s", stmt.keyword, stmt.arg)
    arg = qualify_name(stmt)

    if stmt.parent.keyword != "list":
        result = {
            arg: {
                "type": "list",
                "description": preprocess_string(stmt.search_one("description").arg),
                "elements": "dict",
                "suboptions": [],
            }
        }
    else:
        result = {
            "type": "dict",
            "suboptions": {arg: {"type": "list", "suboptions": []}},
        }

    if hasattr(stmt, "i_children"):
        for child in stmt.i_children:
            if child.keyword in producers:
                logging.debug("keyword hit on: %s %s", child.keyword, child.arg)
                if stmt.parent.keyword != "list":
                    result[arg]["suboptions"].append(producers[child.keyword](child))
                else:
                    result["suboptions"][arg]["suboptions"].append(
                        producers[child.keyword](child)
                    )
            else:
                logging.debug("keyword miss on: %s %s", child.keyword, child.arg)
    logging.debug("In produce_list for %s, returning %s", stmt.arg, result)
    return result


def produce_leaf_list(stmt):
    logging.debug("in produce_leaf_list: %s %s", stmt.keyword, stmt.arg)
    arg = qualify_name(stmt)
    type_stmt = stmt.search_one("type")
    type_id = type_stmt.arg

    if types.is_base_type(type_id) or type_id in _other_type_trans_tbl:
        type_str = produce_type(type_stmt)
        result = {arg: {"type": "list", "elements": "dict", "suboptions": [type_str]}}
    else:
        logging.debug(
            "Missing mapping of base type: %s %s, type: %s",
            stmt.keyword,
            stmt.arg,
            type_id,
        )
        result = {arg: {"type": "list", "suboptions": [{"type": "str"}]}}
    return result


def produce_container(stmt):
    logging.debug("in produce_container: %s %s", stmt.keyword, stmt.arg)
    arg = qualify_name(stmt)

    if stmt.parent.keyword != "list":
        result = {arg: {"type": "dict", "suboptions": {}}}
    else:
        result = {
            "type": "dict",
            "suboptions": {arg: {"type": "dict", "suboptions": {}}},
        }

    if hasattr(stmt, "i_children"):
        for child in stmt.i_children:
            if child.keyword in producers:
                logging.debug("keyword hit on: %s %s", child.keyword, child.arg)
                if stmt.parent.keyword != "list":
                    result[arg]["suboptions"].update(producers[child.keyword](child))
                else:
                    result["suboptions"][arg]["suboptions"].update(
                        producers[child.keyword](child)
                    )
            else:
                logging.debug("keyword miss on: %s %s", child.keyword, child.arg)
    logging.debug("In produce_container, returning %s", result)
    return result


def produce_choice(stmt):
    logging.debug("in produce_choice: %s %s", stmt.keyword, stmt.arg)

    result = {}

    # https://tools.ietf.org/html/rfc6020#section-7.9.2
    for case in stmt.search("case"):
        if hasattr(case, "i_children"):
            for child in case.i_children:
                if child.keyword in producers:
                    logging.debug(
                        "keyword hit on (long version): %s %s", child.keyword, child.arg
                    )
                    result.update(producers[child.keyword](child))
                else:
                    logging.debug("keyword miss on: %s %s", child.keyword, child.arg)

    # Short ("case-less") version
    #  https://tools.ietf.org/html/rfc6020#section-7.9.2
    for child in stmt.substmts:
        logging.debug("checking on keywords with: %s %s", child.keyword, child.arg)
        if child.keyword in ["container", "leaf", "list", "leaf-list"]:
            logging.debug(
                "keyword hit on (short version): %s %s", child.keyword, child.arg
            )
            result.update(producers[child.keyword](child))

    logging.debug("In produce_choice, returning %s", result)
    return result


producers = {
    # "module":     produce_module,
    "container": produce_container,
    "list": produce_list,
    "leaf-list": produce_leaf_list,
    "leaf": produce_leaf,
    "choice": produce_choice,
}

_numeric_type_trans_tbl = {
    # https://tools.ietf.org/html/draft-ietf-netmod-yang-json-02#section-6
    "int8": ("int", None),
    "int16": ("int", None),
    "int32": ("int", "int32"),
    "int64": ("int", "int64"),
    "uint8": ("int", None),
    "uint16": ("int", None),
    "uint32": ("int", "uint32"),
    "uint64": ("int", "uint64"),
}


def numeric_type_trans(dtype):
    trans_type = _numeric_type_trans_tbl[dtype][0]
    # Should include format string in return value
    # tformat = _numeric_type_trans_tbl[dtype][1]
    return {"type": trans_type}


def string_trans(stmt):
    logging.debug("in string_trans with stmt %s %s", stmt.keyword, stmt.arg)
    result = {"type": "str"}
    return result


def enumeration_trans(stmt):
    logging.debug("in enumeration_trans with stmt %s %s", stmt.keyword, stmt.arg)
    result = {"type": "str", "choices": []}
    for enum in stmt.search("enum"):
        result["choices"].append(enum.arg)
    logging.debug("In enumeration_trans for %s, returning %s", stmt.arg, result)
    return result


def bits_trans(stmt):
    logging.debug("in bits_trans with stmt %s %s", stmt.keyword, stmt.arg)
    result = {"type": "str"}
    return result


def boolean_trans(stmt):
    logging.debug("in boolean_trans with stmt %s %s", stmt.keyword, stmt.arg)
    result = {"type": "boolean"}
    return result


def empty_trans(stmt):
    logging.debug("in empty_trans with stmt %s %s", stmt.keyword, stmt.arg)
    result = {"type": "list", "suboptions": [{"type": "null"}]}
    # Likely needs more/other work per:
    #  https://tools.ietf.org/html/draft-ietf-netmod-yang-json-10#section-6.9
    return result


def union_trans(stmt):
    logging.debug("in union_trans with stmt %s %s", stmt.keyword, stmt.arg)
    result = {"oneOf": []}
    for member in stmt.search("type"):
        member_type = produce_type(member)
        result["oneOf"].append(member_type)
    return result


def instance_identifier_trans(stmt):
    logging.debug(
        "in instance_identifier_trans with stmt %s %s", stmt.keyword, stmt.arg
    )
    result = {"type": "str"}
    return result


def leafref_trans(stmt):
    logging.debug("in leafref_trans with stmt %s %s", stmt.keyword, stmt.arg)
    # TODO: Need to resolve i_leafref_ptr here
    result = {"type": "str"}
    return result


_other_type_trans_tbl = {
    # https://tools.ietf.org/html/draft-ietf-netmod-yang-json-02#section-6
    "string": string_trans,
    "enumeration": enumeration_trans,
    "bits": bits_trans,
    "boolean": boolean_trans,
    "empty": empty_trans,
    "union": union_trans,
    "instance-identifier": instance_identifier_trans,
    "leafref": leafref_trans,
}


def other_type_trans(dtype, stmt):
    return _other_type_trans_tbl[dtype](stmt)


def qualify_name(stmt):
    # From: draft-ietf-netmod-yang-json
    # A namespace-qualified member name MUST be used for all members of a
    # top-level JSON object, and then also whenever the namespaces of the
    # data node and its parent node are different.  In all other cases, the
    # simple form of the member name MUST be used.
    if stmt.parent.parent is None:  # We're on top
        pfx = stmt.i_module.arg
        logging.debug("In qualify_name with: %s %s on top", stmt.keyword, stmt.arg)
        return pfx + ":" + stmt.arg
    if stmt.top.arg != stmt.parent.top.arg:  # Parent node is different
        pfx = stmt.top.arg
        logging.debug(
            "In qualify_name with: %s %s and parent is different",
            stmt.keyword,
            stmt.arg,
        )
        return pfx + ":" + stmt.arg
    return stmt.arg
