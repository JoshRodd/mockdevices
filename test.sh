#!/bin/bash

make install &&
sshpass -p 'asapass' ssh -q -o StrictHostKeyChecking=no -o CheckHostIP=no -o UserKnownHostsFile=/dev/null asa@::1
