#!/bin/bash

# asabin/asabin-test.sh

ASABINDIR="$(pwd)"
ASABIN="$ASABINDIR"/"$1"

if [ ! -x "$ASABIN" ]; then
	echo "Cannot execute target $ASABIN"
	exit 1
fi

"$ASABIN" | grep -qe "Welcome to the fake ASA shell, asash"
rc=$?

if [ "$rc" != "0" ]; then
	echo "Did not print the expected output."
	exit 1
fi

# No tests written yet. Pretending to pass anyway.
