#!/bin/bash

USER_FORWARDING=/etc/pf.anchors/org.user.forwarding
SERIAL=$$
PF_CONF=/etc/pf.conf
LOCAL_VM_ADDR=192.168.60.100

#echo mkdir -p "$(dirname ${USER_FORWARDING})" || exit
mkdir -p "$(dirname ${USER_FORWARDING})" || exit
#echo touch ${USER_FORWARDING}.${SERIAL} || exit
touch ${USER_FORWARDING}.${SERIAL} || exit

cat >${USER_FORWARDING}.${SERIAL} <<EOT
rdr pass inet proto tcp from any to any port 80 -> 127.0.0.1 port 8080
rdr pass inet proto tcp from any to any port 443 -> ${LOCAL_VM_ADDR} port 443
EOT
rc=$?; if [ $rc -gt 0 ]; then exit $rc; fi

if [ -f ${USER_FORWARDING} ]; then
#	echo cmp ${USER_FORWARDING} ${USER_FORWARDING}.${SERIAL}
	cmp ${USER_FORWARDING} ${USER_FORWARDING}.${SERIAL}
	rc=$?; if [ "$rc" -gt 2 ]; then exit $rc; fi
	if [ "$rc" -eq 0 ]; then
		echo "The \`${USER_FORWARDING}' file already was created and is valid."
#		echo rm -f ${USER_FORWARDING}.${SERIAL}
		rm -f ${USER_FORWARDING}.${SERIAL}
	elif [ "$rc" -eq 1 ]; then
		echo "The \`${USER_FORWARDING}' file already was created but is not valid."
		echo "Please compare it with \`${USER_FORWARDING}.${SERIAL}'."
		exit 1
	else # $rc -eq 2
#		echo mv ${USER_FORWARDING}.${SERIAL} ${USER_FORWARDING} || exit
		mv ${USER_FORWARDING}.${SERIAL} ${USER_FORWARDING} || exit
	fi
fi

ADDITION='load anchor "org.user.forwarding" from "/etc/pf.anchors/org.user.forwarding"'
ADDITION_GREP="^${ADDITION//./\\.}$"

#echo grep \'"${ADDITION_GREP}"\' ${PF_CONF}
grep "${ADDITION_GREP}" ${PF_CONF}
rc=$?
if [ "$rc" -gt 1 ]; then exit $rc; fi
if [ "$rc" -eq 0 ]; then
	echo The additions to \`${PF_CONF}\" are already present.
else
	cp "${PF_CONF}" "${PF_CONF}.$SERIAL" || exit
#	echo printf \'"%s\n"\' \'"${ADDITION}"\' \>\> "${PF_CONF}.${SERIAL}" || exit
	printf "%s\n" "${ADDITION}" >> "${PF_CONF}.${SERIAL}" || exit
#	echo mv "${PF_CONF}.${SERIAL}" "${PF_CONF}" || exit
	mv "${PF_CONF}.${SERIAL}" "${PF_CONF}" || exit
#	{
#		read ln
#		printf "%s\n" "$ln"
#	} < <(tail -1 ${PF_CONF})
fi

#echo pfctl -vnf "${USER_FORWARDING}" || exit
pfctl -vnf "${USER_FORWARDING}" || exit

cat <<"EOT"
    Now modify /System/Library/LaunchDaemons/com.apple.pfctl.plist from

    <array>
        <string>pfctl</string>
        <string>-f</string>
        <string>/etc/pf.conf</string>
    </array>

    to

    <array>
        <string>pfctl</string>
        <string>-e</string>
        <string>-f</string>
        <string>/etc/pf.conf</string>
    </array>

    You have to disable System Integrity Protection to accomplish this. After editing the file reenable SIP. After rebooting your Mac pf will be enabled (that's the -e option).

    Alternatively you may create your own launch daemon similar to the answer here: Using Server 5.0.15 to share internet WITHOUT internet sharing.

After a system update or upgrade some of the original files above may have been replaced and you have to reapply all changes.

If you want to forward across different interfaces you have to enable this in /etc/sysctl.conf:

net.inet.ip.forwarding=1
net.inet6.ip6.forwarding=1

EOT
