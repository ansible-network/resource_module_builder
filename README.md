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
export PYANG_PLUGINPATH=$PWD/pyang-plugin
cd yangs/ws5
pyang -f ansible ciena-waveserver-system.yang > ../../models/waveserver5/system.yml
pyang -f ansible ciena-waveserver-xcvr.yang > ../../models/waveserver5/xcvr.yml
pyang -f ansible ciena-waveserver-interfaces.yang > ../../models/waveserver5/interfaces.yml
pyang -f ansible ciena-waveserver-aaa.yang > ../../models/waveserver5/aaa.yml
pyang -f ansible ciena-waveserver-module.yang > ../../models/waveserver5/module.yml
pyang -f ansible ciena-waveserver-port.yang > ../../models/waveserver5/port.yml
pyang -f ansible ciena-waveserver-snmp.yang > ../../models/waveserver5/snmp.yml
pyang -f ansible ciena-waveserver-chassis.yang > ../../models/waveserver5/chassis.yml
pyang -f ansible ciena-waveserver-ptp.yang > ../../models/waveserver5/ptp.yml
# Paste the output of that into the model's yml file
# Generate the module code
ansible-playbook generate_saos10.yml
ansible-playbook generate_waveserver5.yml
```
