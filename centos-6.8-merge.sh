#!/bin/bash

# 0.1.0

TUFINOS=TufinOS-2.13
CENTOS=CentOS-6.8
CENTOS_RPM_URL="http://mirror.centos.org/centos/6.8/os/x86_64/Packages/centos-release-6-8.el6.centos.12.3.x86_64.rpm"
CENTOS_RPM_FILE="centos-release-6-8.el6.centos.12.3.x86_64.rpm"
CENTOS_RPM=centos-release
EPEL_RPM_URL="http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm"
EPEL_RPM_FILE="epel-release-6-8.noarch.rpm"
EPEL_RPM=epel-release

if [ "$1" == "--python3-symlinks" ]; then
	(
		cd /usr/local/bin
		ls *3.6* >/dev/null 2>&1 || exit 1
		for x in *3.6*; do
			ln -s "$x" "$(echo "$x" | sed s'/3\.6/3/'g)" || exit 1
		done
	) || exit 1
	echo Symlinks created. Test by running /usr/local/bin/python3
fi

if [ "$1" != "" -a "$1" != "--uninstall" -a "$1" != "--install" -a "$1" != "--doctor" -a "$1" != "--reinstall" ]; then
	cat >&2 <<EOT
Adds a full CentOS 6.8 installation to TufinOS 2.13, or uninstalls it.

Usage: $0 [--uninstall | --reinstall | --python3-symlinks] [--doctor]

The default operation is to install. To prove the new set up works, man, man-pages, and supporting
libraries (xz and xz-lzma-compat) will be installed.

If --uninstall is given, the additions will be removed. This will not work if any optional
packages are present other thn the four listed above. You can check for new packages by 
comparing the file in /etc/"$TUFINOS".packages with the output from: rpm -qa, and then
removing any packages that have been added.

--reinstall is the same as running --uninstall and then immediately running --install.

The --doctor option retains the "$TUFINOS" /etc/redhat-release file, which can improve
compatibility with programs that expect to be installed on TufinOS, not CentOS.

--python3-symlinks makes symlinks from python 3.6 or 3.6.1 to aliases like "python3"
in /usr/local/bin.

EOT
	exit 0
fi

if [ "$1" == "--uninstall" -o "$1" == "--reinstall" ]; then

	rpm -e man man-pages xz xz-lzma-compat || (
		yum install man man-pages xz xz-lzma-compat || exit
		rpm -e man man-pages xz xz-lzma-compat || exit
	)

	rpm -e "$CENTOS_RPM" "$EPEL_RPM" || exit

	mv -f /etc/TufinOS-Media.repo_yum.repos.d_removed /etc/yum.repos.d/TufinOS-Media.repo || exit

	for x in /etc/issue /etc/issue.net /etc/redhat-release /etc/system-release; do
		mv -f "$x"."$TUFINOS" "$x" || exit
	done
	rm /etc/tufinos-release || exit
	ln -sf redhat-release /etc/tufinos-release || exit

	echo $CENTOS has been removed and this is now back to being a base $TUFINOS system.

fi
if [ "$1" == "" -o "$1" == "--install" -o "$1" == "--reinstall" -o "$1" == "--doctor" ]; then

	rpm -qa > /etc/"$TUFINOS".packages.$$
	
	for x in /etc/issue /etc/issue.net /etc/redhat-release /etc/system-release; do
		if [ ! -f "$x"."$TUFINOS" ]; then
			cp -f "$x" "$x"."$TUFINOS" || exit
		fi
	done
	rm /etc/tufinos-release || exit
	cp /etc/redhat-release."$TUFINOS" /etc/tufinos-release || exit
	
	if ! rpm -K --nosignature "$CENTOS_RPM_FILE" 2>/dev/null >&2; then
		curl -L -O "$CENTOS_RPM_URL" || exit
		rpm -K --nosignature "$CENTOS_RPM_FILE" || exit
	fi
	rpm --force -i "$CENTOS_RPM_FILE" || exit
	
	if ! rpm -K --nosignature "$EPEL_RPM_FILE" 2>/dev/null >&2; then
		curl -L -O "$EPEL_RPM_URL" || exit
		rpm -K --nosignature "$EPEL_RPM_FILE" || exit
	fi
	rpm --force -i "$EPEL_RPM_FILE" || exit

	for x in /etc/issue /etc/issue.net /etc/redhat-release /etc/system-release; do
		if [ -f "$x".rpmnew ]; then
			mv -f "$x".rpmnew "$x" || exit
		fi
	done
	
	if [ -f /etc/yum.repos.d/TufinOS-Media.repo ]; then
		mv -f /etc/yum.repos.d/TufinOS-Media.repo /etc/TufinOS-Media.repo_yum.repos.d_removed || exit
	fi

	cp -f /etc/issue.net."$TUFINOS" /etc/issue.net || exit
	cp -f /etc/issue."$TUFINOS" /etc/issue || exit

	if [ "$1" == "--doctor" -o "$2" == "--doctor" ]; then
		cp -f /etc/redhat-release."$TUFINOS" /etc/redhat-release || exit
	fi
	
	yum install man man-pages xz xz-lzma-compat || exit

	mv -f /etc/"$TUFINOS".packages.$$ /etc/"$TUFINOS".packages || exit

	echo You now have a full $CENTOS system with manual pages installed.
	echo Try running \`man cat\' to test it.

fi
