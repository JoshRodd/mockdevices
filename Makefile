# mockdevices/Makefile

VERSION=1.0
CC=clang
CFLAGSO=-O4 -Oz -Ofast -DNDEBUG
CFLAGS=-g -O0 -DDEBUG
PREFIX=/usr/local
README_FILE="README-${CUSTOMER}.md"
CHANGELOG_FILE="CHANGELOG"

all:	bin/asabin bin/asash_prefixed.sh bin/check_install_prefixed.sh

debug:	asabin bin/asash_prefixed.sh bin/check_install_prefixed.sh

bin/asabin_prefixed.c:	asabin.c
	mkdir -p bin/
	sed '/ prefix match$$/'"s;/usr/local;$(PREFIX);g" asabin.c > bin/asabin_prefixed.c

bin/check_install_prefixed.sh:	check_install.sh
	mkdir -p bin/
	sed '/ prefix match$$/'"s;/usr/local;$(PREFIX);g" check_install.sh > bin/check_install_prefixed.sh

bin/asash_prefixed.sh:	asash.sh
	mkdir -p bin/
	sed '/ prefix match$$/'"s;/usr/local;$(PREFIX);g" asash.sh > bin/asash_prefixed.sh

asabin:	bin/asabin_prefixed.c Makefile
	$(CC) $(CFLAGS) bin/asabin_prefixed.c -o asabin

bin/asabin:	bin/asabin_prefixed.c Makefile
	mkdir -p bin/
	$(CC) $(CFLAGSO) bin/asabin_prefixed.c -o bin/asabin
	strip bin/asabin

dist:	bin/asabin bin/asash_prefixed.sh asamock.py get_sshd_port.py interactive_asa.py asa_config.py install-shells.sh deploy-xinetd-ssh.sh bin/check_install_prefixed.sh mockdevices_requirements.txt mockdevices_required_rpms.txt mockdevices_required_rpms_rhel7.txt
	mkdir -p dist/
	install -m 755 bin/asabin dist/
	install -m 755 bin/asash_prefixed.sh dist/asash
	install -m 755 bin/check_install_prefixed.sh dist/mockdevices_check_install.sh
	install -m 755 asamock.py get_sshd_port.py interactive_asa.py asa_config.py install-shells.sh deploy-xinetd-ssh.sh dist/
	install -m 644 mockdevices_requirements.txt mockdevices_required_rpms.txt mockdevices_required_rpms_rhel7.txt dist/
	echo ${VERSION} > dist/"${CUSTOMER}-version"
	install -m644 ${README_FILE} "dist/"
	install -m644 ${CHANGELOG_FILE} "dist/"
	mkdir -p distd"$(PREFIX)/bin"
	cp -av dist/* distd"$(PREFIX)/bin"

install:	dist
	mkdir -p "$(PREFIX)/bin"
	install dist/* "$(PREFIX)/bin"
	rm "$(PREFIX)/bin/asamock.py"
	rm "$(PREFIX)/bin/asa_config.py"
	rm "$(PREFIX)/bin/interactive_asa.py"
	rm "$(PREFIX)/bin/get_sshd_port.py"
	ln -sf `pwd`/asamock.py "$(PREFIX)/bin"
	ln -sf `pwd`/asa_config.py "$(PREFIX)/bin"
	ln -sf `pwd`/interactive_asa.py "$(PREFIX)/bin"
	ln -sf `pwd`/get_sshd_port.py "$(PREFIX)/bin"

uninstall:
	rm -f "$(PREFIX)/bin/"CHANGELOG
	rm -f "$(PREFIX)/bin/"README-mockdevices.md
	rm -f "$(PREFIX)/bin/"asa_config.py
	rm -f "$(PREFIX)/bin/"asabin
	rm -f "$(PREFIX)/bin/"asamock.py
	rm -f "$(PREFIX)/bin/"asash
	rm -f "$(PREFIX)/bin/"deploy-xinetd-ssh.sh
	rm -f "$(PREFIX)/bin/"get_sshd_port.py
	rm -f "$(PREFIX)/bin/"install-shells.sh
	rm -f "$(PREFIX)/bin/"interactive_asa.py
	rm -f "$(PREFIX)/bin/"mockdevices-version
	rm -f "$(PREFIX)/bin/"mockdevices_check_install.sh
	rm -f "$(PREFIX)/bin/"mockdevices_required_rpms.txt
	rm -f "$(PREFIX)/bin/"mockdevices_required_rpms_rhel7.txt
	rm -f "$(PREFIX)/bin/"mockdevices_requirements.txt

clean:
	rm -rf *.dSYM bin/ dist/ asabin distd/ *.run *.bz2

TITLE_PLACE_HOLDER=__TITLE_PLACE_HOLDER__
MD5SUM_PLACEHOLDER=__MD5SUM_PLACE_HOLDER__
SHA256SUM_PLACEHOLDER=__SHA256SUM_PLACE_HOLDER__
CUSTOMER=mockdevices
SOLUTION_TITLE=mockdevices
SOLUTION_PACKAGE_NAME=setup_${CUSTOMER}

package:	${SOLUTION_PACKAGE_NAME}.tar.bz2
	echo Solution is: "${SOLUTION_PACKAGE_NAME}-${VERSION}.run"

package_install:	package
	./${SOLUTION_PACKAGE_NAME}-${VERSION}.run

package_uninstall:	package
	./${SOLUTION_PACKAGE_NAME}-${VERSION}.run --uninstall

package_release:	package
	scp ${SOLUTION_PACKAGE_NAME}-${VERSION}.run jerodd@rodd.us:rodd.us/ee18/ggp

${SOLUTION_PACKAGE_NAME}.tar.bz2: ${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp
	$(eval TARGET_SHA256SUM:=$(shell cat "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp.sha256sum"))
	$(eval TARGET_MD5SUM:=$(shell cat "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp.md5sum"))
	(./make_preamble.sh "${SOLUTION_PACKAGE_NAME}-${VERSION}.run"; cat bash-common-new.sh | sed -e "s/${MD5SUM_PLACEHOLDER}/${TARGET_MD5SUM}/g" -e "s/${SHA256SUM_PLACEHOLDER}/${TARGET_SHA256SUM}/g" -e "s/${TITLE_PLACE_HOLDER}/${SOLUTION_TITLE}/g" | bzip2 -9 | base64 -w 76; cat customer_self_extract_end.sh) > "${SOLUTION_PACKAGE_NAME}.sh.tmp"
	(cat "${SOLUTION_PACKAGE_NAME}.sh.tmp"; base64 -w 76 < "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp") > "${SOLUTION_PACKAGE_NAME}.run"
	rm -f ${SOLUTION_PACKAGE_NAME}.*tmp ${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp* ${CUSTOMER}-version
	mv "${SOLUTION_PACKAGE_NAME}.run" "${SOLUTION_PACKAGE_NAME}-${VERSION}.run"
	chmod +x "${SOLUTION_PACKAGE_NAME}-${VERSION}.run"

${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp: dist
	tar -C distd/ -c . | bzip2 -9 > "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp"
	cat "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp" | openssl dgst -md5 -binary | xxd -c 32 -p > "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp.md5sum"
	cat "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp" | openssl dgst -sha256 -binary | xxd -c 32 -p > "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp.sha256sum"
