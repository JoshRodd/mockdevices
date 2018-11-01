#!/bin/bash

diff <(rpm -qa --qf="%{NAME}\n"|grep -v gpg-pubkey|sort) <(cat TufinOS-2.13.packages|sed -r s'/-[0-9.]{3}.*$//'|sort)|grep '^< '|sed s'/< //'
