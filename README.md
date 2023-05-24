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
# Download some yangs for the device type you are working on
ansible-playbook yang_get.yml
# Convert the yangs to json schema
ansible-playbook yang_convert_to_json.yml
# Create the models for the device type you are working on
# Generate the module code
ansible-playbook generate_saos10.yml
```
