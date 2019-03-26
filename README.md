## Resource module models and scaffolder

### To do

1) Improve the model schema
2) Add the example files to the doc string
3) Document the model keys


### Usage

```
pip install ansible
pip install jsonref
```

```
ansible-playbook -e parent=<parent> \
                 -e structure=role \
                 -e model=<model> \
                 site.yml
```
or
```
ansible-playbook -e parent=<parent> \
                 -e structure=collection \
                 -e collection_org=<collection_org> \
                 -e collection_name=<collection_name> \
                 -e model=<model> \
                 site.yml
```
- `parent`: The parent directory in which the files and directories should be placed
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
ansible-playbook -e parent=~/github/rm_example \
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
│   │   └── myos_interfaces.py
│   └── module_utils
│       ├── __init__.py
│       ├── network
│       │   ├── argspec
│       │   │   ├── base.py
│       │   │   └── __init__.py
│       │   └── __init__.py
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
└── roles
 
```
**Role directory layout**

- `network_os`: myos
- `resource`: interfaces

```
ansible-playbook -e parent=~/github/rm_example/roles/my_role \
                 -e structure=role \
                 -e model=models/myos/interfaces/myos_interfaces.yml \
                 site.yml
```

```
└── roles
    └── my_role
        ├── library
        │   ├── __init__.py
        │   └── myos_interfaces.py
        └── module_utils
            ├── __init__.py
            ├── network
            │   ├── argspec
            │   │   ├── base.py
            │   │   └── __init__.py
            │   └── __init__.py
            └── myos
                ├── argspec
                │   ├── facts
                │   │   ├── facts.py
                │   │   └── __init__.py
                │   ├── __init__.py
                │   └── interfaces
                │       ├── __init__.py
                │       └── interfaces.py
                ├── config
                │   ├── base.py
                │   ├── __init__.py
                │   └── interfaces
                │       ├── __init__.py
                │       └── interfaces.py
                ├── facts
                │   ├── base.py
                │   ├── facts.py
                │   ├── __init__.py
                │   └── interfaces
                │       ├── __init__.py
                │       └── interfaces.py
                ├── __init__.py
                └── utils
                    ├── __init__.py
                    └── utils.py
```

**Using the collection layout**

Note: As of 3/26/2019, the following PR needs to be used:
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
```
