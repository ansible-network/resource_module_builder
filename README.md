##  Resource module builder for Ciena

### Overview

Generates modules for:

* Waveserver Ai
* SAOS 10
* Waveserver 5
* RLS

### Resource Module Builder

The playbooks in this project generate modules for Ciena collections using the resource module builder.

Usage:

```bash
pipenv shell
pipenv install git+https://github.com/ansible-network/collection_prep#egg=collection_prep
# modify vars in playbook.yml
ansible-playbook playbook.yml
```
