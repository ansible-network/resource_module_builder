##  Resource module builder for Ciena

### Overview

Waveserver Ai and SAOS models

### Resource Module Builder

The modules in this project were built using the resource module builder.

Usage:

```bash
pip install -r requirements.txt
# modify vars in playbook.yml
ansible-playbook playbook.yml
```

```bash
ansible-playbook -e rm_dest=waveserverai \
                 -e structure=collection \
                 -e collection_org=ciena \
                 -e collection_name=waveserverai \
                 -e model=models/waveserverai/xcvrs/waveserverai_xcvrs.yml \
                 -e transport=netconf \
                 site.yml
```
