#!/bin/bash

# Adds the given number of ports to xinetd's ASA ssh service.
#
# If the --uninstall parameter is passed, removes it.

OPERATION=install
NEWSHELL=""
SHELLSFILE="/etc/xinetd.d/asa-ssh"
DRY_RUN=0
QUIET=0
local_ip=$(grep "$(hostname)" /etc/hosts | awk '{print $1}')
USAGE="Usage: $0 [--uninstall | -d] [-f | --xinetd-file=/etc/xinetd.d/asa-ssh] [-i IP_ADDRESS] NUMPORTS"
while [ "$1" != "" ]; do
	if [ "$1" == "--uninstall" -o "$1" == "-d" ]; then
		OPERATION=uninstall
		shift
	elif [ "$1" == "--install" ]; then
		OPERATION=install
		shift
	elif [ "$1" == "--dry-run" -o "$1" == "-n" ]; then
		DRY_RUN=1
		shift
	elif [ "$1" == "--help" -o "$1" == "--version" ]; then
		echo "$USAGE"
		echo
		echo Adds the given number of ports to xinetd. If the --uninstall
		echo option is set, removes it if it is present.
		echo
		echo The default IP address in use is $local_ip. To use something
		echo else, use the -i option.
		if [ "$1" == "" ]; then
			exit 1
		fi
		exit 0
	elif [ "$1" == "-q" -o "$1" == "--quiet" ]; then
		shift
		QUIET=1
	elif [ "$1" == "-f" -a "$2" != "" ]; then
		shift
		SHELLSFILE="$1"
		shift
	elif [ "${1:0:14}" == "--xinetd-file=" ]; then
		SHELLSFILE=${1:14}
		shift
	elif [ "$1" == "-i" ]; then
		shift
		local_ip="$1"
		shift
	else
		NEWSHELL="$1"
		shift
	fi
done

if [ "$NEWSHELL" == "" -a "$OPERATION" != "uninstall" ]; then
	echo "$USAGE" >&2
	exit 1
fi

if [ "$OPERATION" != "uninstall" ]; then
	if [ "$NEWSHELL" -lt 0 -o "$NEWSHELL" -gt 999 ]; then
		echo "Number of ports is limited to 1 through 999." >&2
		exit 1
	fi
fi

if [ "$OPERATION" == "uninstall" ]; then
	rm -f "$SHELLSFILE"
fi
# Not already there. If installing, we need to append it to the end.
if [ "$DRY_RUN" -eq 1 ]; then
	SHELLSFILE_REAL="$SHELLSFILE"
	SHELLSFILE=/tmp/asa-ssh.$$
fi
NEWSHELL_STORE="$NEWSHELL"
if [ "$OPERATION" == "install" ]; then
	curport=22001
	local_ip_name="$(printf "%s\n" "$local_ip" | tr . _)"
	printf "%s\n%s\n" "# default: on" "# description: Emulates a Cisco ASA or Meraki device accessed via SSH." > "$SHELLSFILE"
	while [ "$NEWSHELL" -gt 0 ]; do
		local_ip_name_with_port="$local_ip_name"_"$curport"
		cat <<EOT

service asa$curport
{
        flags           = REUSE
        socket_type     = stream
        wait            = no
        user            = root
        server          = /usr/sbin/sshd
        server_args     = -i
        log_on_failure  += USERID
        disable         = no
        bind            = $local_ip
        type            = UNLISTED
        port            = $curport
}
EOT
		NEWSHELL="$(expr $NEWSHELL - 1)"
		curport="$(expr $curport + 1)"
	done >> "$SHELLSFILE"
fi
if [ "$DRY_RUN" -ne 1 ]; then
	if [ "$OPERATION" == "uninstall" ]; then
		printf "Terminating xinetd\n"
	fi
	service xinetd reload
	service xinetd start
else
	cmp "$SHELLSFILE_REAL" "$SHELLSFILE" >/dev/null 2>/dev/null
	if [ $? -ne 0 ]; then
		rm "$SHELLSFILE"
		if [ "$QUIET" != 1 ]; then
			echo The current xinetd installation needs updated.
			echo Please run this command:
			printf "\t%s %d\n" "$0" "$NEWSHELL_STORE"
		fi
		exit 1
	fi
	rm "$SHELLSFILE"
fi
exit 0
