# mockdevices/Makefile

VERSION=1.0
CC=clang
CFLAGSO=-O4 -Oz -Ofast -DNDEBUG
CFLAGS=-g -O0 -DDEBUG
PREFIX=/usr/local

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
	mkdir -p distd/"$(PREFIX)/bin"
	cp -av dist/* distd/"$(PREFIX)/bin"
	tar -C distd -c . | bzip2 -9 > mockdevices_dist.tar.bz2
	rm -rf distd/

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

clean:
	rm -rf *.dSYM bin/ dist/ asabin distd/

TITLE_PLACE_HOLDER=__TITLE_PLACE_HOLDER__
MD5SUM_PLACEHOLDER=__MD5SUM_PLACE_HOLDER__
SHA256SUM_PLACEHOLDER=__SHA256SUM_PLACE_HOLDER__
CUSTOMER=mockdevices
SOLUTION_TITLE=mockdevices
SOLUTION_PACKAGE_NAME=setup_${CUSTOMER}
README_FILE="README-${CUSTOMER}.md"
CHANGELOG_FILE="CHANGELOG"

${SOLUTION_PACKAGE_NAME}.tar.bz2: ${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp
	$(eval TARGET_SHA256SUM:=$(shell cat "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp.sha256sum"))
	$(eval TARGET_MD5SUM:=$(shell cat "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp.md5sum"))
	@(./make_preamble.sh "${SOLUTION_PACKAGE_NAME}-${VERSION}.run"; sed 1,2d ../../templates/bash-common-new.sh) | cat - ./customer_self_extract_start.sh ./custom_install_script.sh ./customer_self_extract_end.sh > "${SOLUTION_PACKAGE_NAME}.sh.tmp"
	@sed -i.backup "s/${MD5SUM_PLACEHOLDER}/${TARGET_MD5SUM}/g" "${SOLUTION_PACKAGE_NAME}.sh.tmp"
	@rm "${SOLUTION_PACKAGE_NAME}.sh.tmp.backup"
	@sed -i.backup "s/${SHA256SUM_PLACEHOLDER}/${TARGET_SHA256SUM}/g" "${SOLUTION_PACKAGE_NAME}.sh.tmp"
	@rm "${SOLUTION_PACKAGE_NAME}.sh.tmp.backup"
	@sed -i.backup "s/${TITLE_PLACE_HOLDER}/${SOLUTION_TITLE}/g" "${SOLUTION_PACKAGE_NAME}.sh.tmp"
	@rm "${SOLUTION_PACKAGE_NAME}.sh.tmp.backup"
	@cat "${SOLUTION_PACKAGE_NAME}.sh.tmp" "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp" > "${SOLUTION_PACKAGE_NAME}.run"
	@rm -f ${SOLUTION_PACKAGE_NAME}.*tmp ${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp* ${CUSTOMER}-version
	@mv "${SOLUTION_PACKAGE_NAME}.run" "${SOLUTION_PACKAGE_NAME}-${VERSION}.run"
	@chmod +x "${SOLUTION_PACKAGE_NAME}-${VERSION}.run"
	@echo Solution is: "${SOLUTION_PACKAGE_NAME}-${VERSION}.run"

${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp: dist
	@echo ${VERSION} > dist/"${CUSTOMER}-version"
	@install -m644 "${README_FILE}" "dist/"
	@install -m644 "${CHANGELOG}" "dist/"
	@tar -cjvf "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp" -C "dist/"
	@cat "${SOLUTION_PACKAGE_NAME}.tar.bz2.tmp" | openssl dgst -md5 -binary | xxd -c 32 -p > "${SOLUTION_PACKAGE_NAME}.tar.bz.tmp.md5sum"
	@cat "${SOLUTION_PACKAGE_NAME}.tar.bz.tmp" | openssl dgst -sha256 -binary | xxd -c 32 -p > "${SOLUTION_PACKAGE_NAME}.tar.bz.tmp.sha256sum"
