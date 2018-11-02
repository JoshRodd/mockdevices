#!/bin/bash

RUNFILE="$1"
CUSTOMER="$(basename "$(pwd)")"
CUSTOMER_DISPLAY_NAME="$(printf "%s\n" "${CUSTOMER}" | sed 's/_AND_/\&/g' | sed '/.*_AND_.*/! s/_/ /' )"
SOLUTION_TITLE="${CUSTOMER_DISPLAY_NAME} Solution"
SOLUTION_PACKAGE_NAME="setup_${CUSTOMER}_solution"
SOLUTION_FILE_LIST+="${CUSTOMER}-version"
SOLUTION_VERSION_FILE="${CUSTOMER}-version"
SOLUTION_BUILD_FILE="${CUSTOMER}-build"

if [ ! -f "$SOLUTION_VERSION_FILE" ]; then
	if [ ! -f ./Makefile ]; then
		echo "The file $SOLUTION_VERSION_FILE is missing. Please create it." >&2
		exit 1
	else
		SOLUTION_VERSION="$(grep '^VERSION=' ./Makefile | sed -e s'/^VERSION=//' -e s'/#.*$//' -e s'/^[^0-9\.]*\([0-9\.][0-9\.]*\).*$/\1/' | tr -dc 0-9.)"
		if [ "$SOLUTION_VERSION" == "" ]; then
			echo "The file $SOLUTION_VERSION_FILE is missing and Makefile does not contain a valid VERSION= line." >&2
			exit 1
		fi
	fi
else
	SOLUTION_VERSION="$(cat "$SOLUTION_VERSION_FILE")"
fi
if [ ! -f "$SOLUTION_BUILD_FILE" ]; then
	echo 0 > "$SOLUTION_BUILD_FILE" || exit
fi
SOLUTION_BUILD="$(cat "$SOLUTION_BUILD_FILE" | tr -dc 0-9; echo)"
SOLUTION_BUILD=$[$SOLUTION_BUILD + 1]
echo "$SOLUTION_BUILD" > "$SOLUTION_BUILD_FILE" || exit

BUILD_TIMESTAMP="$(TZ=EST5EDT LC_TIME=C date +'%Y-%m-%d %T %z %Z')"
BUILD_TIMESTAMP_SERIAL="$(TZ=EST5EDT LC_TIME=C date +'%Y%m%d%H%M%S')"

cat <<EOT
#!/bin/bash

# Package: $CUSTOMER_DISPLAY_NAME
# Version: $SOLUTION_VERSION build $SOLUTION_BUILD on $USER@$HOSTNAME at $BUILD_TIMESTAMP
# Runfile: $RUNFILE

if [ "\$1" == "--readme" ]; then cat | less <<"=========="
EOT
cat README-$CUSTOMER.md
cat <<EOT
==========
exit 0; fi
export B_SOURCE="\${BASH_SOURCE[0]}"; echo "
EOT
