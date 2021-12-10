## Resource module builder

### Overview

The resource module builder is an Ansible Playbook that helps developers scaffold and maintain an Ansible network resource module.

***Note***: 
For scaffolding cli-based Resource Modules that leverage the new network parsing engine please use the [CLI_RM_BUILDER](https://github.com/ansible-network/cli_rm_builder) collection. 

**Capabilities**
- Use a defined model to scaffold a resource module directory layout and initial class files.
- Scaffold either an Ansible role or a collection.
- Subsequent uses of the Resource Module Builder (RMB) will only replace the module arspec and file containing the module doc string.
- Complex examples can be stored along side the model in the same directory.
- Maintain the model as the source of truth for the module and use RMB to update the source files as needed.
- Generates working sample modules for both `<network_os>_<resource>` and `<network_os>_facts`


### Usage

```
pip install -r requirements.txt
```

```
ansible-playbook -e rm_dest=<destination for modules and module utils> \
                 -e structure=role \
                 -e model=<model> \
                 site.yml
```
or
```
ansible-playbook -e rm_dest=/home/jgroom/src/ansible_collections/ciena/waveserverai/ \
                 -e structure=collection \
                 -e collection_org=ciena \
                 -e collection_name=waveserverai \
                 -e model=/home/jgroom/src/ansible_collections/ciena/waveserverai/resource_module_models/xcvr/waveserverai_xcvr.yml \
                 -e transport=netconf \
                 site.yml
```

```
PATH_TO_ANSIBLE_COLLECTIONS_DIR=/home/$USER/src/ansible_collections/ciena/saos10
ansible-playbook -e rm_dest=saos10 \
                 -e structure=collection \
                 -e collection_org=ciena \
                 -e collection_name=saos10 \
                 -e model=$PATH_TO_ANSIBLE_COLLECTIONS_DIR/resource_module_models/classifiers/saos10_classifiers.yml \
                 -e transport=netconf \
                 site.yml
```

- `rm_dest`: The directory in which the files and directories for the resource module and facts modules should be placed
- `structure`: The directory layout to be generated (role|collection)
  - `role`: Generate a role directory layout
  - `collection`: Generate a collection directory layout
- `collection_org`: The organization of the collection, required when `structure=collection`
- `collection_name`: The name of the collection, required when `structure=collection`
- `model`: The path to the model file

### Model

See the `models` directory for an example.

### Examples

**Collection directory layout**

- `network_os`: myos
- `resource`: interfaces

```
ansible-playbook -e rm_dest=~/github/rm_example \
                 -e structure=collection \
                 -e collection_org=cidrblock \
                 -e collection_name=my_collection \
                 -e model=models/myos/interfaces/myos_interfaces.yml \
                 site.yml
```

```
├── docs
├── playbooks
├── plugins
│   ├── action
│   ├── filter
│   ├── inventory
│   ├── modules
│   │   ├── __init__.py
│   │   ├── myos_facts.py
│   │   └── myos_interfaces.py
│   └── module_utils
│       ├── __init__.py
│       └── network
│           ├── __init__.py
│           └── myos
│               ├── argspec
│               │   ├── facts
│               │   │   ├── facts.py
│               │   │   └── __init__.py
│               │   ├── __init__.py
│               │   └── interfaces
│               │       ├── __init__.py
│               │       └── interfaces.py
│               ├── config
│               │   ├── base.py
│               │   ├── __init__.py
│               │   └── interfaces
│               │       ├── __init__.py
│               │       └── interfaces.py
│               ├── facts
│               │   ├── base.py
│               │   ├── facts.py
│               │   ├── __init__.py
│               │   └── interfaces
│               │       ├── __init__.py
│               │       └── interfaces.py
│               ├── __init__.py
│               └── utils
│                   ├── __init__.py
│                   └── utils.py
├── README.md
├── roles

 
```
**Role directory layout**

- `network_os`: myos
- `resource`: interfaces

```
ansible-playbook -e rm_dest=~/github/rm_example/roles/my_role \
                 -e structure=role \
                 -e model=models/myos/interfaces/myos_interfaces.yml \
                 site.yml
```

```
roles
└── my_role
    ├── library
    │   ├── __init__.py
    │   ├── myos_facts.py
    │   └── myos_interfaces.py
    ├── LICENSE.txt
    ├── module_utils
    │   ├── __init__.py
    │   └── network
    │       ├── __init__.py
    │       └── myos
    │           ├── argspec
    │           │   ├── facts
    │           │   │   ├── facts.py
    │           │   │   └── __init__.py
    │           │   ├── __init__.py
    │           │   └── interfaces
    │           │       ├── __init__.py
    │           │       └── interfaces.py
    │           ├── config
    │           │   ├── base.py
    │           │   ├── __init__.py
    │           │   └── interfaces
    │           │       ├── __init__.py
    │           │       └── interfaces.py
    │           ├── facts
    │           │   ├── base.py
    │           │   ├── facts.py
    │           │   ├── __init__.py
    │           │   └── interfaces
    │           │       ├── __init__.py
    │           │       └── interfaces.py
    │           ├── __init__.py
    │           └── utils
    │               ├── __init__.py
    │               └── utils.py
    └── README.md
```

**Using the collection layout**

```
git clone git@github.com:ansible/ansible.git
cd ansible
git fetch origin pull/52194/head:collection_test
git checkout collection_test
```

link the generated collection to `~/.ansible/collections/ansible_collections/<collection_org>/<collection_name>`

```
ln -s ~/github/rm_example ~/.ansible/collections/ansible_collections/cidrblock/my_collection
 ```

`site.yml`
 ```
 - hosts: myos101
   gather_facts: False
   tasks:
   - cidrblock.my_collection.myos_interfaces:
     register: result
   - debug:
       var: result
   - cidrblock.my_collection.myos_facts:
   - debug:
       var: ansible_network_resources

```

**Using the role layout**

`site.yml`
```
- hosts: myos101
  gather_facts: False
  roles:
  - my_role

- hosts: myos101
  gather_facts: False
  tasks:
  - myos_interfaces:
    register: result
  - debug:
      var: result
  - myos_facts:
  - debug:
      var: ansible_network_resources
```

### Resource Module Structure/Workflow

**Module**

`library/<ansible_network_os>_<resource>.py`.

- Import `module_utils` resource package and calls `execute_module` API
```
def main():
    result = <resource_package>(module).execute_module()
```

**Module Argspec**

`module_utils/<ansible_network_os>/argspec/<resource>/`.

- Argspec for the resource.

**Facts**

`module_utils/<ansible_network_os>/facts/<resource>/`.

- Populate facts for the resource.
- Entry in `module_utils/<ansible_network_os>/facts/facts.py` for `get_facts` API to keep
  `<ansible_network_os>_facts` module and facts gathered for the resource module in sync
  for every subset.
- Entry under the imports to register the Module's fact class- 
  `from ansible_collections.<ansible_network_org>.<ansible_network_os>.plugins.module_utils.network.
  <ansible_network_os>.facts.<resource>.<resource> import (<Resource>Facts,)`
- An entry in the global variable `FACT_RESOURCE_SUBSETS` is required in order to add it to the resource
  subsets as `<resource>=<Resource>Facts`.

**Module Package in module_utils**

`module_utils/<ansible_network_os>/<config>/<resource>/`.

- Implement `execute_module` API that loads the config to device and generates the result with
  `changed`, `commands`, `before` and `after` keys.
- Call `get_facts` API that returns the `<resource>` config facts or return the diff if the
  device has onbox diff support.
- Compare facts gathered and given key-values if diff is not supported.
- Generate final config.

**Utils**

`module_utils/<ansible_network_os>/utils`.

- Utilities for the` <ansible_network_os>` platform.

### Developer Notes

The tests rely on a role generated by the resource module builder. After changes to the resource module builder, the role should be regenerated and the tests modified and run as needed.  To generate the role after changes:

```
rm -rf rmb_tests/roles/my_role
ansible-playbook -e rm_dest=./rmb_tests/roles/my_role \
                 -e structure=role \
                 -e model=models/myos/interfaces/myos_interfaces.yml \
                 site.yml
```
