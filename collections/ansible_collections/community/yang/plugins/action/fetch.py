# (c) 2020, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import json

from ansible.module_utils import basic
from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase
from ansible.module_utils._text import to_text, to_bytes
from ansible.module_utils.connection import Connection
from ansible.module_utils.six import iteritems
from ansible.utils.path import unfrackpath, makedirs_safe
from ansible_collections.community.yang.plugins.module_utils.fetch import (
    SchemaStore,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    convert_doc_to_ansible_module_kwargs,
    dict_merge,
)
from ansible_collections.community.yang.plugins.modules.fetch import (
    DOCUMENTATION,
)


ARGSPEC_CONDITIONALS = {"mutually_exclusive": [["name", "all"]]}
VALID_CONNECTION_TYPES = ["ansible.netcommon.netconf"]


def generate_argspec():
    """ Generate an argspec
    """
    argspec = convert_doc_to_ansible_module_kwargs(DOCUMENTATION)
    argspec = dict_merge(argspec, ARGSPEC_CONDITIONALS)
    return argspec


class ActionModule(ActionBase):
    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._result = {}

    def _fail_json(self, msg):
        """ Replace the AnsibleModule fai_json here
        :param msg: The message for the failure
        :type msg: str
        """
        msg = msg.replace("(basic.py)", self._task.action)
        raise AnsibleActionFail(msg)

    def _debug(self, msg):
        """Output text using ansible's display

        :param msg: The message
        :type msg: str
        """
        msg = "<{phost}> [fetch][action] {msg}".format(
            phost=self._playhost, msg=msg
        )
        self._display.vvvv(msg)

    def _check_argspec(self):
        """ Load the doc and convert
        Add the root conditionals to what was returned from the conversion
        and instantiate an AnsibleModule to validate
        """
        argspec = generate_argspec()
        basic._ANSIBLE_ARGS = to_bytes(
            json.dumps({"ANSIBLE_MODULE_ARGS": self._task.args})
        )
        basic.AnsibleModule.fail_json = self._fail_json
        basic.AnsibleModule(**argspec)

    def run(self, tmp=None, task_vars=None):
        if self._play_context.connection.split(".")[-1] != "netconf":
            return {
                "failed": True,
                "msg": "Connection type %s is not valid for this module. Valid connection type is one of '%s'."
                % (
                    self._play_context.connection,
                    ", ".join(VALID_CONNECTION_TYPES),
                ),
            }
        self._playhost = task_vars.get("inventory_hostname")

        self._check_argspec()
        if self._result.get("failed"):
            return self._result

        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        schema = self._task.args.get("name")
        dir_path = self._task.args.get("dir")
        continue_on_failure = self._task.args.get("continue_on_failure", False)
        socket_path = self._connection.socket_path
        conn = Connection(socket_path)

        capabilities = json.loads(conn.get_capabilities())
        server_capabilities = capabilities.get("server_capabilities", [])

        if "netconf-monitoring" not in "\n".join(server_capabilities):
            raise AnsibleActionFail(
                "remote netconf server does not support required capability"
                " to fetch yang schema (urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring)."
            )

        try:
            ss = SchemaStore(conn, debug=self._debug)
        except ValueError as exc:
            raise AnsibleActionFail(
                to_text(exc, errors="surrogate_then_replace")
            )
        except Exception as exc:
            raise AnsibleActionFail(
                "Unhandled exception from fetch SchemaStore. Error: {err}".format(
                    err=to_text(exc, errors="surrogate_then_replace")
                )
            )

        result["fetched"] = dict()
        if continue_on_failure:
            result["failed_yang_models"] = []
        total_count = 0
        try:
            supported_yang_modules = ss.get_schema_description()
            if schema:
                if schema == "all":
                    for item in supported_yang_modules:
                        changed, counter = ss.run(
                            item, result, continue_on_failure
                        )
                        total_count += counter
                else:
                    changed, total_count = ss.run(
                        schema, result, continue_on_failure
                    )
        except ValueError as exc:
            raise AnsibleActionFail(
                to_text(exc, errors="surrogate_then_replace")
            )
        except Exception as exc:
            raise AnsibleActionFail(
                "Unhandled exception from get schema description. Error: {err}".format(
                    err=to_text(exc, errors="surrogate_then_replace")
                )
            )

        if schema:
            if dir_path:
                yang_dir = unfrackpath(dir_path)
                makedirs_safe(yang_dir)
                for name, content in iteritems(result["fetched"]):
                    file_path = os.path.join(yang_dir, "%s.yang" % name)
                    with open(file_path, "w+") as fp:
                        fp.write(content)
            result["number_schema_fetched"] = total_count
            result["changed"] = True
        else:
            supported_yang_modules.sort()
            result["supported_yang_modules"] = supported_yang_modules
            result["changed"] = False
            result["number_schema_fetched"] = 0

        return result
