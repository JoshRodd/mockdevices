#!/bin/bash

sshpass -p 'joshpass' ssh -q -o StrictHostKeyChecking=no -o CheckHostIP=no -o UserKnownHostsFile=/dev/null josh@127.200.2.2 /Users/josh/Documents/src/mockdevices/asash
