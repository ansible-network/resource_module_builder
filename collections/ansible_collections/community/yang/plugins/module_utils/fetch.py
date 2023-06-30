# -*- coding: utf-8 -*-
# Copyright 2020 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re
import sys

is_py2 = sys.version[0] == "2"
if is_py2:
    import Queue as queue
else:
    import queue

from ansible.module_utils._text import to_text
from ansible.module_utils.connection import ConnectionError

try:
    import xmltodict

    HAS_XMLTODICT = True
except ImportError:
    HAS_XMLTODICT = False


class SchemaStore(object):
    def __init__(self, conn, debug=None):
        self._conn = conn
        self._schema_cache = []
        self._all_schema_list = None
        self._all_schema_identifier_list = []
        self._debug = debug
        self._latest_revision_dates = {}  # Store the latest revision dates

    def get_schema_description(self):
        if not HAS_XMLTODICT:
            raise ValueError(
                "xmltodict is required to store response in json format "
                "but does not appear to be installed. "
                "It can be installed using `pip install xmltodict`"
            )
        get_filter = """
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" type="subtree">
          <netconf-state xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring">
            <schemas/>
          </netconf-state>
        </filter>
        """
        try:
            resp = self._conn.get(filter=get_filter)
        except ConnectionError as e:
            raise ValueError(to_text(e))

        res_json = xmltodict.parse(resp, dict_constructor=dict)
        if "rpc-reply" in res_json:
            self._all_schema_list = res_json["rpc-reply"]["data"][
                "netconf-state"
            ]["schemas"]["schema"]
        else:
            self._all_schema_list = res_json["data"]["netconf-state"][
                "schemas"
            ]["schema"]

        for index, schema_list in enumerate(self._all_schema_list):
            identifier = schema_list["identifier"]
            self._all_schema_identifier_list.append(identifier)

            # Store the latest revision date
            if 'version' in schema_list:
                self._latest_revision_dates[identifier] = schema_list['version']

        return self._all_schema_identifier_list

    def get_one_schema(self, schema_id, revision_date, result, continue_on_error=False):
        print(f"Fetching schema {schema_id} with revision {revision_date}")  # Debug print
        if self._all_schema_list is None:
            self.get_schema_description()

        found = False
        data_model = None

        schema_cache_entry = {}
        for index, schema_list in enumerate(self._all_schema_list):
            if schema_id == schema_list["identifier"]:
                # Add a check for the revision date
                if 'version' in schema_list and schema_list['version'] == revision_date:
                    found = True
                    break

        if schema_id in self._all_schema_identifier_list:
            print(f"Found schema {schema_id}. {revision_date}")
            xml_request = f'<get-schema xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring"><identifier>{schema_id}</identifier><version>{revision_date}</version></get-schema>'
            try:
                response = self._conn.dispatch(xml_request)
            except ConnectionError as e:
                raise ValueError(to_text(e))
            res_json = xmltodict.parse(response, dict_constructor=dict)
            if "rpc-reply" in res_json:
                data_model = res_json["rpc-reply"]["data"]["#text"]
            if "nc:rpc-reply" in res_json:
                data_model = res_json["nc:rpc-reply"]["data"]["#text"]
            if self._debug:
                self._debug("Fetched '%s' yang model" % schema_id)
            result["fetched"][schema_id] = data_model
            self._schema_cache.append(schema_cache_entry)
        else:
            if not continue_on_error:
                raise ValueError("Fail to fetch '%s' yang model" % schema_id)
            else:
                if self._debug:
                    self._debug("Fail to fetch '%s' yang model" % schema_id)
                result["failed_yang_models"].append(schema_id)

        return found, data_model

    def get_schema_and_dependants(
        self, schema_id, result, continue_on_failure=False
    ):
        # Get the latest revision date for this schema
        revision_date = self._latest_revision_dates.get(schema_id)
        print(f"Fetching schema and dependants for {schema_id} with revision {revision_date}")  # Debug print

        try:
            found, data_model = self.get_one_schema(
                schema_id, revision_date, result, continue_on_failure
            )
        except ValueError as exc:
            raise ValueError(exc)

        if found:
            result["fetched"][schema_id] = data_model
            importre = re.compile(r"import (.+) {")
            all_found = importre.findall(data_model)
            all_found = [re.sub("['\"]", "", imp) for imp in all_found]

            return all_found
        else:
            return []

    def run(self, schema_id, result, continue_on_failure=False):
        # Get the latest revision date for this schema
        revision_date = self._latest_revision_dates.get(schema_id)

        changed = False
        counter = 1
        sq = queue.Queue()
        sq.put((schema_id, revision_date))  # Include the revision date in the queue

        while sq.empty() is not True:
            schema_id, revision_date = sq.get()  # Extract the schema_id and revision_date from the queue
            if schema_id in result["fetched"]:
                counter -= 1
                continue

            schema_dlist = self.get_schema_and_dependants(
                schema_id, result, continue_on_failure
            )
            for schema_id in schema_dlist:
                # Get the latest revision date for this schema
                revision_date = self._latest_revision_dates.get(schema_id)
                if schema_id not in result["fetched"]:
                    sq.put((schema_id, revision_date))  # Include the revision date in the queue
                    changed = True
                    counter += 1

        return changed, counter
