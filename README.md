##  Resource module builder for Ciena

### Overview

Waveserver Ai and SAOS models

### Resource Module Builder

The modules in this project were built using the resource module builder.

Usage:

```
pip install -r requirements.txt
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

```bash
ansible-playbook -e rm_dest=saos10 \
                 -e structure=collection \
                 -e collection_org=ciena \
                 -e collection_name=saos10 \
                 -e model=models/saos10/classifiers/saos10_classifiers.yml \
                 -e transport=netconf \
                 site.yml
```
