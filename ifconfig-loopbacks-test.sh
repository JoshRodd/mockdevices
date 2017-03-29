#!/bin/bash

# ifconfig-loopbacks-test.sh

IFCONFIGLOOPBACKSDIR="$(pwd)"
IFCONFIGLOOPBACKS="$IFCONFIGLOOPBACKSDIR"/"$1"

if [ ! -x "$IFCONFIGLOOPBACKS" ]; then
	echo "Cannot execute target $IFCONFIGLOOPBACKS"
	exit 1
fi

"$IFCONFIGLOOPBACKS" --dry-run --force | wc -l | grep -qe "1000"
rc=$?

if [ "$rc" != "0" ]; then
	echo "Did not print the expected output."
	exit 1
fi
