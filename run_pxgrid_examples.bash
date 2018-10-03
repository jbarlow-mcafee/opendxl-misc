#!/bin/bash

IP_ADDRESS="192.168.56.4"
MAC_ADDRESS="00:15:5d:84:2e:0a"

echo "updating ip and mac address references in test files"
for f in $(ls sample/basic/*.py);
do
  sed -i "s/<SPECIFY_IP_ADDRESS>/${IP_ADDRESS}/g; s/<SPECIFY_MAC_ADDRESS>/${MAC_ADDRESS}/g" $f
done

echo "anc apply mac"
python sample/basic/basic_anc_apply_endpoint_policy_by_mac_example.py

echo "anc get mac"
python sample/basic/basic_anc_get_endpoint_by_mac_example.py

echo "anc clear mac"
python sample/basic/basic_anc_clear_endpoint_policy_by_mac_example.py

echo "anc apply ip"
python sample/basic/basic_anc_apply_endpoint_policy_by_ip_example.py

echo "anc get ip"
python sample/basic/basic_anc_get_endpoint_by_ip_example.py

echo "anc clear ip"
python sample/basic/basic_anc_clear_endpoint_policy_by_ip_example.py

echo "anc retrieve policy by name"
python sample/basic/basic_anc_retrieve_policy_by_name_example.py

echo "anc retrieve all policies"
python sample/basic/basic_anc_retrieve_all_policies_example.py

echo "eps send mitigation by ip"
python sample/basic/basic_eps_send_mitigation_action_by_ip_example.py

echo "eps send mitigation by mac"
python sample/basic/basic_eps_send_mitigation_action_by_mac_example.py
