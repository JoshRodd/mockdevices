#!/bin/bash

MOCKDEVICES_PREFIX=/usr/local # prefix match

[[ :$PATH: == *:"$MOCKDEVICES_PREFIX"/bin:* ]] || export PATH="$MOCKDEVICES_PREFIX"/bin:"$PATH"

if [ -d /opt/tufin/securitysuite/ps ]; then
	export TUFIN_PS_HOME=/opt/tufin/securitysuite/ps
	[[ :$PATH: == *:"$TUFIN_PS_HOME"/bin:* ]] || export PATH="$TUFIN_PS_HOME"/bin:"$PATH"
	[[ :$PATH: == *:"$TUFIN_PS_HOME"/python/bin:* ]] || export PATH="$TUFIN_PS_HOME"/python/bin:"$PATH"
fi

exec -a asash "$MOCKDEVICES_PREFIX"/bin/asamock.py "$@"
