#!/bin/bash

make install >/dev/null &&
#sshpass -p 'asapass' ssh -q -o StrictHostKeyChecking=no -o CheckHostIP=no -o UserKnownHostsFile=/dev/null asa@56.0.0.5
ssh -q -o StrictHostKeyChecking=no -o CheckHostIP=no -o UserKnownHostsFile=/dev/null asa@56.0.0.5
