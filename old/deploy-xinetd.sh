#!/bin/bash

# Adds the given number of ports to xinetd.
#
# If the --uninstall parameter is passed, removes it.

OPERATION=install
NEWSHELL=""
SHELLSFILE="/etc/xinetd.d/asa"
local_ip=$(grep "$(hostname)" /etc/hosts | awk '{print $1}')
USAGE="Usage: $0 [--uninstall | -d] [-f | --xinetd-file=/etc/xinetd.d/asa] [-i IP_ADDRESS] NUMPORTS"
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
		echo Adds the given number of ports to xinetd. If the --uninstall
		echo option is set, removes it if it is present.
		echo
		echo The default IP address in use is $local_ip. To use something
		echo else, use the -i option.
		if [ "$1" == "" ]; then
			exit 1
		fi
		exit 0
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

if [ "$NEWSHELL" == "" ]; then
	echo "$USAGE" >&2
	exit 1
fi

if [ "$NEWSHELL" -lt 0 -o "$NEWSHELL" -gt 999 ]; then
	echo "Number of ports is limited to 1 through 999." >&2
	exit 1
fi

if [ "$OPERATION" == "uninstall" ]; then
	rm "$SHELLSFILE"
fi
# Not already there. If installing, we need to append it to the end.
if [ "$OPERATION" == "install" ]; then
	curport=23001
	local_ip_name="$(printf "%s\n" "$local_ip" | tr . _)"
	printf "%s\n%s\n" "# default: on" "# description: Emulates a Cisco ASA or Meraki device accessed via telnet." > "$SHELLSFILE"
	while [ "$NEWSHELL" -gt 0 ]; do
		local_ip_name_with_port="$local_ip_name"_"$curport"
		ln -f /usr/local/bin/asabin214_0_0_1 /usr/local/bin/asabin$local_ip_name_with_port || exit 1
		cat <<EOT

service asa$curport
{
        flags           = REUSE
        socket_type     = stream
        wait            = no
        user            = asa
        server          = /usr/sbin/in.telnetd
        server_args     = -n -L /usr/local/bin/asabin$local_ip_name_with_port
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
service xinetd reload
service xinetd start
