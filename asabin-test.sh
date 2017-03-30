#!/bin/bash

# asabin/asabin-test.sh

ASABINDIR="$(pwd)"
ASABIN="$ASABINDIR"/"$1"

if [ ! -x "$ASABIN" ]; then
	echo "Cannot execute target $ASABIN"
	exit 1
fi

SSH_CONNECTION="::1 12345 ::1 22" "$ASABIN" | fgrep -qe "##################################################"
rc=$?

if [ "$rc" != "0" ]; then
	echo "Did not print the expected output."
	exit 1
fi

# No tests written yet. Pretending to pass anyway.
