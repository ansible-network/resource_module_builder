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
```

#### Builing a new module/collection
```
ansible-playbook -e rm_dest=<destination for modules and module utils> \
                 -e collection_org=<collection_org> \
                 -e collection_name=<collection_name> \
                 -e docstring=<model> \
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

### Model

See the `models` directory for an example.

### Examples

**Collection directory layout**

- `network_os`: myos
- `resource`: interfaces

```
├── docs
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
├── tests


**Using the collection layout**

```
pip install ansible-base==2.10.0b1 --user
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

### Resource Module Structure/Workflow [TO-DO]


### Developer Notes [TO-DO]
