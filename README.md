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
pip install git+https://github.com/ansible-network/collection_prep.git
# Download some yangs for the device type you are working on
ansible-playbook yang_get.yml
# Convert the yangs to RMB json
./generate_ymls.sh
# Move the output of the into the model's yml file
RESOURCE=system && python3 insert.py -i models/waveserver5/$RESOURCE.yml -r models/waveserver5/$RESOURCE/waveserver5_$RESOURCE.yml -k waveserver_$RESOURCE
RESOURCE=pm && python3 insert.py -i models/waveserver5/$RESOURCE.yml -r models/waveserver5/$RESOURCE/waveserver5_$RESOURCE.yml -k waveserver_$RESOURCE
RESOURCE=aaa && python3 insert.py -i models/waveserver5/$RESOURCE.yml -r models/waveserver5/$RESOURCE/waveserver5_$RESOURCE.yml -k waveserver_$RESOURCE

RESOURCE=xcvrs && python3 insert.py -i models/waveserver5/$RESOURCE.yml -r models/waveserver5/$RESOURCE/waveserver5_$RESOURCE.yml -k waveserver_$RESOURCE.suboptions.$RESOURCE
RESOURCE=ports && python3 insert.py -i models/waveserver5/$RESOURCE.yml -r models/waveserver5/$RESOURCE/waveserver5_$RESOURCE.yml -k waveserver_$RESOURCE.suboptions.$RESOURCE
RESOURCE=ptps && python3 insert.py -i models/waveserver5/$RESOURCE.yml -r models/waveserver5/$RESOURCE/waveserver5_$RESOURCE.yml -k waveserver_$RESOURCE.suboptions.$RESOURCE

# Generate the module code
ansible-playbook generate_saos10.yml
ansible-playbook generate_waveserver5.yml
```
