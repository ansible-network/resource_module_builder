#!/bin/bash
export PYANG_PLUGINPATH=/home/jgroom/src/resource_module_builder/pyang-plugin
cd yangs/ws5
pyang -f ansible ciena-waveserver-system.yang > ../../models/waveserver5/system.yml
pyang -f ansible ciena-waveserver-xcvr.yang > ../../models/waveserver5/xcvrs.yml
pyang -f ansible ciena-waveserver-interfaces.yang > ../../models/waveserver5/interfaces.yml
pyang -f ansible ciena-waveserver-aaa.yang > ../../models/waveserver5/aaa.yml
pyang -f ansible ciena-waveserver-module.yang > ../../models/waveserver5/modules.yml
pyang -f ansible ciena-waveserver-port.yang > ../../models/waveserver5/ports.yml
pyang -f ansible ciena-waveserver-snmp.yang > ../../models/waveserver5/snmp.yml
pyang -f ansible ciena-waveserver-chassis.yang > ../../models/waveserver5/chassis.yml
pyang -f ansible ciena-waveserver-ptp.yang > ../../models/waveserver5/ptps.yml
pyang -f ansible ciena-waveserver-pm.yang > ../../models/waveserver5/pm.yml
pyang -f ansible ciena-waveserver-snmp.yang > ../../models/waveserver5/snmp.yml
cd ../..
cd yangs/saos10
pyang -f ansible ciena-mef-classifier.yang > ../../models/saos10/classifier.yml
pyang -f jsonschema ciena-mef-classifier.yang > ../../models/saos10/classifier.json
pyang -f ansible ciena-mef-fd.yang > ../../models/saos10/fd.yml
pyang -f ansible ciena-mef-fp.yang > ../../models/saos10/fp.yml
