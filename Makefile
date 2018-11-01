# mockdevices/Makefile

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
