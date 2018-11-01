# mockdevices/Makefile

CC=clang
CFLAGSO=-O4 -Oz -Ofast -DNDEBUG
CFLAGS=-g -O0 -DDEBUG
PREFIX=/usr/local
ALT_PREFIX=/opt/local

all:	asabin asash asamock.py

asabin:	asabin.c Makefile
	$(CC) $(CFLAGS) asabin.c -o asabin

bin/asabin:	asabin.c Makefile
	mkdir -p bin
	$(CC) $(CFLAGSO) asabin.c -o bin/asabin
	strip bin/asabin

uninstall:
	rm -f "$(PREFIX)/bin/asabin"
	rm -f "$(PREFIX)/bin/asash"
	rm -f "$(PREFIX)/bin/asamock.py"
	rm -f "$(ALT_PREFIX)/bin/asabin"
	rm -f "$(ALT_PREFIX)/bin/asash"
	rm -f "$(ALT_PREFIX)/bin/asamock.py"
	./install-shells.sh --uninstall "$(PREFIX)/bin/asabin"

install:	bin/asabin asash asamock.py
	mkdir -p "$(PREFIX)/bin"
	install -m 755 bin/asabin "$(PREFIX)/bin"
	install -m 755 asash "$(PREFIX)/bin"
	ln -sf /usr/local/src/mockdevices/asamock.py "$(PREFIX)/bin/asamock.py"
	install -m 755 ifconfig-loopbacks "$(PREFIX)/bin"
	mkdir -p "$(ALT_PREFIX)"/bin
	ln -sf ../../../usr/local/bin/asabin "$(ALT_PREFIX)/bin/asabin"
	ln -sf /usr/local/src/mockdevices/asamock.py "$(ALT_PREFIX)/bin/asamock.py"
	ln -sf ../../../usr/local/bin/asash "$(ALT_PREFIX)/bin/asash"
	./install-shells.sh "$(PREFIX)/bin/asabin"

commit:	test install clean Makefile
	git commit --all
	git push

clean:
	rm -f asabin asabin.o
	rm -rf asabin.dSYM bin

# Tests don't work unless it's fully installed.
test:	./asabin-test.sh ./ifconfig-loopbacks-test.sh ifconfig-loopbacks asabin bin/asabin Makefile ./asamock.py install
	true
#	echo enable | ./asabin-test.sh asabin
#	echo enable | ./asabin-test.sh bin/asabin
#	./test_ifconfig-loopbacks.sh ifconfig-loopbacks
#	./asamock.py

$(DEBUG).SILENT:	test
