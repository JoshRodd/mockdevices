#!/bin/bash

# Adds the shell passed as a parameter to /etc/shells.
#
# If the --uninstall parameter is passed, removes it.

OPERATION=install
NEWSHELL=""
SHELLSFILE="/etc/shells"
USAGE="Usage: $0 [--uninstall | -d] [-f | --shells-file=/etc/shells] /path/to/shell"
while [ "$1" != "" ]; do
	if [ "$1" == "--uninstall" -o "$1" == "-d" ]; then
		OPERATION=uninstall
		shift
	elif [ "$1" == "--install" ]; then
		OPERATION=install
		shift
	elif [ "$1" == "--help" -o "$1" == "--version" ]; then
		echo "$USAGE"
		echo
		echo Adds the given shell to /etc/shells. If the --uninstall
		echo option is set, removes it if it is present.
		if [ "$1" == "" ]; then
			exit 1
		fi
		exit 0
	elif [ "$1" == "-f" -a "$2" != "" ]; then
		shift
		SHELLSFILE="$1"
		shift
	elif [ "${1:0:14}" == "--shells-file=" ]; then
		SHELLSFILE=${1:14}
		shift
	else
		NEWSHELL="$1"
		shift
	fi
done

if [ "$NEWSHELL" == "" ]; then
	echo "$USAGE" >&2
	exit 1
fi

if [ \( ! -x "$NEWSHELL" \) -a "$OPERATION" != "uninstall" ]; then
	echo The program \`"$NEWSHELL"\' cannot be executed. >&2
	exit 1
fi

# Convert the shell requested into a (basic regular expression) pattern.
pat="$NEWSHELL"
pat=${pat//\\/\\\\}
pat=${pat//\//\\\/}
pat=${pat//^/\\^}
pat=${pat//\$/\\\$}
pat=${pat//./\\.}
pat=${pat//\*/\\\*}
pat="^$pat\$"

grep -q "$pat" "$SHELLSFILE"
rc=$?
if [ "$rc" -gt 1 ]; then exit $rc; fi
# Already there. If uninstalling, we need to remove it.
if [ "$rc" -eq 0 -a "$OPERATION" == "uninstall" ]; then
	if [ ! -w "$SHELLSFILE" ]; then
		echo The file \`"$SHELLSFILE"\' cannot be written. Are you root\? >&2
		exit 1
	fi
	sed -i "" /"$pat"/d "$SHELLSFILE" || exit
fi
# Not already there. If installing, we need to append it to the end.
if [ "$rc" -eq 1 -a "$OPERATION" == "install" ]; then
	if [ ! -w "$SHELLSFILE" ]; then
		echo The file \`"$SHELLSFILE"\' cannot be written. Are you root\? >&2
		exit 1
	fi
	printf "%s\n" "$NEWSHELL" >> "$SHELLSFILE"
fi
