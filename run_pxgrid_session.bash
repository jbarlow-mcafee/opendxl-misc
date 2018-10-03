#!/bin/bash

REMOTE_IP=192.168.56.4
REMOTE_MAC=00:15:5d:84:2e:0a
ISE_SERVER=192.168.25.10
SESSION_LIFETIME=5

JAVA_CMD="java -cp RadiusSimulator.jar"
ISE_CREDS="-DUSERNAME=root -DPASSWORD=password"
CALLING_STATION_ID="-DCALLING_STATION_ID=${REMOTE_MAC}"
FRAME_IP="-DFRAMED_IP_ADDRESS=${REMOTE_IP} -DFRAMED_IP_MASK=255.255.255.0"
SESSION_ID="-DAUDIT_SESSION_ID=${RANDOM}"
RADIUS_CMD="${JAVA_CMD} ${ISE_CREDS} ${FRAME_IP} ${CALLING_STATION_ID} ${SESSION_ID}"

echo "Authenticating ${REMOTE_IP}"
set -x
$RADIUS_CMD RadiusAuthentication $ISE_SERVER
set +x

echo "Starting session for ${REMOTE_IP}"
set -x
$RADIUS_CMD RadiusAccountingStart $ISE_SERVER
set +x

echo "Sleeping in active session for ${SESSION_LIFETIME}"
sleep $SESSION_LIFETIME

echo "Stopping session for ${REMOTE_IP}"
set -x
$RADIUS_CMD RadiusAccountingStop $ISE_SERVER
set +x
