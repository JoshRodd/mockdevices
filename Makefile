# mockdevices/Makefile

CC=clang
CFLAGSO=-O4 -Oz -Ofast -DNDEBUG
CFLAGS=-g -O0 -DDEBUG
PREFIX=/usr/local

all:	asabin asash_prefixed asamock.py

asabin_prefixed.c:	asabin.c
	sed '/ prefix match$/' s';/usr/local;'"$(PREFIX)"';g' asabin.c > asabin_prefixed.c

check_install_prefixed.sh:	check_install.sh
	sed '/ prefix match$/' s';/usr/local;'"$(PREFIX)"';g' check_install.sh > check_install_prefixed.sh

asash_prefixed.sh:	asash.sh
	sed '/ prefix match$/' s';/usr/local;'"$(PREFIX)"';g' asash.sh > asash_prefixed.sh

asabin:	asabin_prefixed.c Makefile
	$(CC) $(CFLAGS) asabin_prefixed.c -o asabin

bin/asabin:	asabin_prefixed.c Makefile
	mkdir -p bin
	$(CC) $(CFLAGSO) asabin_prefixed.c -o bin/asabin
	strip bin/asabin

uninstall:
	rm -f "$(PREFIX)/bin/asabin"
	rm -f "$(PREFIX)/bin/asash"
	rm -f "$(PREFIX)/bin/asamock.py"

dist:	bin/asabin asash_prefixed.sh asamock.py check_install_prefixed.sh
	mkdir -p dist/
	install -m 755 bin/asabin dist/
	install -m 755 asash_prefixed.sh dist/asash
	install -m 755 check_install_prefixed.sh dist/mockdevices_check_install.sh
	install -m 755 asamock.py dist/asamock.py

install:	bin/asabin asash_prefixed.sh asamock.py check_install_prefixed.sh
	mkdir -p "$(PREFIX)/bin"
	install -m 755 bin/asabin "$(PREFIX)/bin"
	install -m 755 asash_prefixed.sh "$(PREFIX)/bin/asash"
	ln -sf /usr/local/src/mockdevices/asamock.py "$(PREFIX)/bin/asamock.py"
	ln -sf /usr/local/src/mockdevices/asamock.py "$(ALT_PREFIX)/bin/asamock.py"

clean:
	rm -f asabin asabin_prefixed.o asabin_prefixed.c check_install_prefixed.sh
	rm -rf asabin.dSYM bin
