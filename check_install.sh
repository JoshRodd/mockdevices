#!/bin/bash

BASE_DIR="$(dirname "$(perl -MCwd -e 'print Cwd::abs_path shift' "$0")")"/
NUM_PORTS=999

PREFIX=/usr/local # prefix match
# The password below is: asapass
PASSWORD_C='$6$X51nKmyZ$8jvXBLXCGkKOvbJg5etTz.3RLBUffkYgATrhuDF.4BB1tJ8nY6huPmCG7JTQyAaWbCO30T1/xlUbbXc9jHAN/1'

OPERATION="check"
if [ "$1" == "--version" ]; then
	printf "mockdevices check_install.sh v1.0\n"
	exit 0
elif [ "$1" == "--help" ]; then
	cat <<EOT
$0

Checks that the mockdevices installation is working properly. If
an improper installation is found, the correct commands to properly
install will be displayed.
EOT
	exit 0
elif [ "$1" == "" ]; then
	:
elif [ "$1" == "--install" ]; then
	OPERATION="install"
elif [ "$1" == "--check" ]; then
	OPERATION="check"
elif [ "$1" == "--uninstall" ]; then
	"$BASE_DIR"/install-shells.sh --uninstall "$PREFIX"/bin/asabin
	"$BASE_DIR"/deploy-xinetd-ssh.sh --uninstall
	if [ "$2" == "--force" ]; then
		pip3 uninstall -y -r "$BASE_DIR"mockdevices_requirements.txt
	fi
	userdel -fr asa
        rm -f "$BASE_DIR"/CHANGELOG
        rm -f "$BASE_DIR"/README-mockdevices.md
        rm -f "$BASE_DIR"/asa_config.py
        rm -f "$BASE_DIR"/asabin
        rm -f "$BASE_DIR"/asamock.py
        rm -f "$BASE_DIR"/asash
        rm -f "$BASE_DIR"/deploy-xinetd-ssh.sh
        rm -f "$BASE_DIR"/get_sshd_port.py
        rm -f "$BASE_DIR"/install-shells.sh
        rm -f "$BASE_DIR"/interactive_asa.py
        rm -f "$BASE_DIR"/mockdevices-version
        rm -f "$BASE_DIR"/mockdevices_required_rpms.txt
        rm -f "$BASE_DIR"/mockdevices_required_rpms_rhel7.txt
        rm -f "$BASE_DIR"/mockdevices_requirements.txt
        rm -f "$BASE_DIR"/mockdevices_check_install.sh
	printf "Uninstalled.\n"
	exit 0
else
	printf "Invalid option %s\n" "$1"
	exit 1
fi

is_ok=1
# Check RPMs
what_release=0
cat /etc/redhat-release | grep -q 'release 7\.'
if [ $? -eq 0 ]; then what_release='RHEL_7'; required_rpms='mockdevices_required_rpms_rhel7.txt'; fi
cat /etc/redhat-release | grep -q 'release 6\.'
if [ $? -eq 0 ]; then what_release='RHEL_6'; required_rpms='mockdevices_required_rpms.txt'; fi
if [ "$what_release" == "0" ]; then
	printf "I can't recognise this system as either a RHEL or CentOS 6 or 7 system.\n"
	printf "Check the /etc/redhat-release file.\n"
	printf "You may manually check the package listing for comparable packages\n"
	printf "in $BASE_DIR/$required_rpms\n"
	printf "if you are running another Linux distribution such as Debian.\n"
	if [ "$OPERATION" == "install" ]; then
		exit 1
	fi
else
count=$(comm -13 <(rpm -qa --qf="%{NAME}\n" | sort) <(cat "$BASE_DIR"/"$required_rpms" | sort) | wc -l)
if [ $count -gt 0 -a "$OPERATION" == "install" ]; then
	yum install -y `cat "$BASE_DIR""$required_rpms"`
	count=$(comm -13 <(rpm -qa --qf="%{NAME}\n" | sort) <(cat "$BASE_DIR"/"$required_rpms" | sort) | wc -l)
fi
if [ $count -gt 0 ]; then
	is_ok=0
	printf "%d packages are missing, as listed in $BASE_DIR""$required_rpms\n" "$count"
	printf "Install them with this command:\n"
	printf '\n\tyum install `cat %s%s`\n' "$BASE_DIR" "$required_rpms"
	exit 1
fi
fi

which python3 2>/dev/null >/dev/null
python3_exe=$?
which python3.6 2>/dev/null >/dev/null
python36_exe=$?

if [ "$python3_exe" -eq 0 ]; then

VERSION_MAJOR="$(python3 --version | awk '{print $2}' | sed s'/^\([0-9][0-9]*\)\.[0-9][0-9]*.*$/\1/')"
VERSION_MINOR="$(python3 --version | awk '{print $2}' | sed s'/^[0-9][0-9]*\.\([0-9][0-9]*\).*$/\1/')"
if [ "$VERSION_MAJOR" -eq 3 -a "$VERSION_MINOR" -eq 4 ]; then
	# For now, tolerate Python 3.4
	:
elif [ "$VERSION_MAJOR" -ne 3 -o "$VERSION_MINOR" -lt 6 ]; then
	printf "Python 3.6 or later is required.\n"
	printf "Make sure older Python versions are uninstalled.\n\n"
#	printf "Try using this command:\n"
#	printf '\n\tyum uninstall `rpm -qa | grep python34`\n'
	if [ "$OPERATION" == "install" ]; then
		exit 1
	fi
fi

fi

if [ "$python36_exe" -eq 0 -a "$python3_exe" -ne 0 -a "$OPERATION" == "install" ]; then
	ln -sf python3.6 /bin/python3
fi
if [ "$python36_exe" -eq 0 -a "$python3_exe" -ne 0 ]; then
	printf "/bin/python3 needs to be a link to /bin/python3.6\n"
	printf "Run this command:\n"
	printf "\n\tln -sf python3.6 /bin/python3\n"
	exit 1
fi

python3 -m pip --version >/dev/null
if [ $? -ne 0 -a "$OPERATION" == "install" ]; then
	python3 -m ensurepip
	python3 -m pip --version >/dev/null
fi
if [ $? -ne 0 ]; then
	printf "The Python 3 PIP doesn't seem to be installed.\n"
	printf "Repair it with this command:\n"
	printf '\n\tpython3 -m ensurepip\n'
	exit 1
fi

# Check PIP packages
count=$((pip3 freeze -r "$BASE_DIR"mockdevices_requirements.txt 3>&2 2>&1 1>&3) 2>/dev/null | grep 'not installed$' | wc -l)
if [ $count -gt 0 ]; then
	if [ "$OPERATION" == "install" ]; then
		pip3 install -r "$BASE_DIR"mockdevices_requirements.txt
	fi
	count=$((pip3 freeze -r "$BASE_DIR"mockdevices_requirements.txt 3>&2 2>&1 1>&3) 2>/dev/null | grep 'not installed$' | wc -l)
fi
if [ $count -gt 0 ]; then
	is_ok=0
	printf "%d PIP packages need to be installed, as listed in $BASE_DIR""mockdevices_requirements.txt\n" "$count"
	printf "Install them with this command:\n"
	printf '\n\tpip3 install -r %smockdevices_requirements.txt\n' "$BASE_DIR"
fi

"$BASE_DIR"/install-shells.sh --check "$PREFIX"/bin/asabin
if [ $? -ne 0 -a "$OPERATION" == "install" ]; then
	"$BASE_DIR"/install-shells.sh "$PREFIX"/bin/asabin
	"$BASE_DIR"/install-shells.sh --check "$PREFIX"/bin/asabin
fi
if [ $? -ne 0 ]; then
	is_ok=0
	printf "/etc/shells doesn't contain %s/bin/asabin\n" "$PREFIX"
	printf "Add it with this command:\n"
	printf "\n\t%sinstall-shells.sh %sbin/asabin\n" "$BASE_DIR" "$PREFIX"
fi

grep -q '^asa:' /etc/passwd
if [ $? -ne 0 -a "$OPERATION" == "install" ]; then
	useradd -d /home/asa asa -s "$PREFIX"/bin/asabin -p "$PASSWORD_C"
	grep -q '^asa:' /etc/passwd
fi
if [ $? -ne 0 ]; then
	is_ok=0
	printf "The asa user doesn't seem to exist.\n"
	printf "Add it with this command:\n"
	printf '\n\tuseradd -d /home/asa asa -s %sbin/asabin\n' "$PREFIX"
	if [ "$OPERATION" == "install" ]; then exit 1; fi
elif [ ! -d ~asa ]; then
	is_ok=0
	printf "The asa user's home directory doesn't seem to exist.\n"
	printf "Add it with this command:\n"
	printf '\n\tmkdir /home/asa\n'
	printf '\n\tchown asa:asa /home/asa\n'
	if [ "$OPERATION" == "install" ]; then exit 1; fi
else
	c="$(grep '^asa:' /etc/passwd | sed -n s'/^asa:x:\([0-9][0-9]*\):\([0-9][0-9]*\):[^:]*:\([^:]*\):\(.*\)$/\3/'p)"
	d="$(grep '^asa:' /etc/passwd | sed -n s'/^asa:x:\([0-9][0-9]*\):\([0-9][0-9]*\):[^:]*:\([^:]*\):\(.*\)$/\4/'p)"
	if [ "$c" != "/home/asa" ]; then
		is_ok=0
		printf "The asa user's home directory is incorrectly set to %s\n" "$c"
		printf "You will need to delete it and recreate it.\n"
		if [ "$OPERATION" == "install" ]; then exit 1; fi
	elif [ "$d" != "$PREFIX/bin/asabin" ]; then
		is_ok=0
		printf "The asa user's shell is incorrectly set to %s\n" "$d"
		printf "Fix it with this command:\n"
		printf '\n\tusermod asa -s $PREFIX/bin/asabin\n'
		if [ "$OPERATION" == "install" ]; then exit 1; fi
	fi
fi

"$BASE_DIR"deploy-xinetd-ssh.sh -q -n "$NUM_PORTS"
if [ $? -ne 0 -a "$OPERATION" == "install" ]; then
	"$BASE_DIR"deploy-xinetd-ssh.sh "$NUM_PORTS"
	"$BASE_DIR"deploy-xinetd-ssh.sh -q -n "$NUM_PORTS"
fi
if [ $? -ne 0 ]; then
	printf "xinetd hasn't been deployed yet properly.\n"
	printf "Run this command:\n"
	printf "\n\tdeploy-xinetd-ssh.sh $NUM_PORTS\n\n"
	is_ok=0
else

	count=$(netstat -an|grep 22[0-9][0-9][0-9].*LISTEN|wc -l)
	if [ $count -ne "$NUM_PORTS" ]; then
		is_ok=0
		printf "Expected to see %d listeners on ports 22001-22999, but saw %d.\n" "$NUM_PORTS" "$count"
		printf "Check the output of netstat -an | grep 22[0-9][0-9][0-9].*LISTEN\n"
		printf "And then try running this command:\n"
		printf "\n\tservice xinetd restart\n"
		if [ "$OPERATION" == "install" ]; then exit 1; fi
	fi

fi

if [ $is_ok -eq 1 ]; then
	if [ "$OPERATION" == "install" ]; then
		printf "Installed successfully.\n"
	else
		printf "Installation appears to be OK.\n"
	fi
	exit 0
else
	exit 1
fi
