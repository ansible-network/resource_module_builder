## Resource module builder

### Overview

The resource module builder is an Ansible Playbook that helps developers scaffold and maintain an Ansible network resource module.

**Capabilities**
- Use a defined model to scaffold a resource module directory layout and initial class files.
- Scaffold an Ansible collection.
- Subsequent uses of the Resource Module Builder (RMB) will only update the module arspec and file containing the module doc string.
- Maintain the module DOCUMENTATION as the source of truth for the module and use RMB to update the source files as needed.
- Generates working sample modules for both `<network_os>_<resource>` and `<network_os>_facts`


### Usage

```
pip install -r requirements.txt
ansible-galaxy collection install ansible.netcommon
```

#### Builing a new module/collection
```
ansible-playbook -e rm_dest=<destination for modules and module utils> \
                 -e collection_org=<collection_org> \
                 -e collection_name=<collection_name> \
                 -e docstring=</path/to/docstring> \
                 -e resource=<resource>
                 site.yml
```

#### Updating an existing module
```
ansible-playbook -e rm_dest=<destination for modules and module utils> \
                 -e collection_org=<collection_org> \
                 -e collection_name=<collection_name> \
                 -e resource=<resource> \
                 site.yml
```

- `rm_dest`: The directory in which the files and directories for the resource module and facts modules should be placed
- `collection_org`: The organization of the collection
- `collection_name`: The name of the collection
- `resource`: The network resource targeted by the module
- `docstring`: The path to the file that contains docstring
- `network_os`: The value of network_os (defaults to `collection_name`)

### Docstrings

See the `docstrings` directory for an example.

### Examples

**Collection directory layout**

- `network_os`: myos
- `resource`: interfaces

```
├── LICENSE
├── README.md
├── docs
├── meta
├── plugins
│   ├── action
│   │   └── __init__.py
│   ├── filter
│   │   └── __init__.py
│   ├── inventory
│   │   └── __init__.py
│   ├── module_utils
│   │   ├── __init__.py
│   │   └── network
│   │       ├── __init__.py
│   │       └── nxos
│   │           ├── __init__.py
│   │           ├── argspec
│   │           │   ├── __init__.py
│   │           │   ├── facts
│   │           │   │   ├── __init__.py
│   │           │   │   └── facts.py
│   │           │   └── interfaces
│   │           │       ├── __init__.py
│   │           │       └── interfaces.py
│   │           ├── config
│   │           │   ├── __init__.py
│   │           │   └── interfaces
│   │           │       ├── __init__.py
│   │           │       └── interfaces.py
│   │           ├── facts
│   │           │   ├── __init__.py
│   │           │   ├── facts.py
│   │           │   └── interfaces
│   │           │       ├── __init__.py
│   │           │       └── interfaces.py
│   │           ├── rm_templates
│   │           │   ├── __init__.py
│   │           │   └── interfaces.py
│   │           └── utils
│   │               ├── __init__.py
│   │               └── utils.py
│   └── modules
│       ├── __init__.py
│       ├── nxos_facts.py
│       └── nxos_interfaces.py
└── tests
```

### Using collections in a playbook

Please refer to [using collections in a playbook](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html#using-collections-in-a-playbook) guide for detailed information.

### Resource Module Structure/Workflow [TO-DO]


### Developer Notes [TO-DO]
