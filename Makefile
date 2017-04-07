# mockdevices/Makefile

CC=cc
CFLAGSO=-O4 -Oz -Ofast -DNDEBUG
CFLAGS=-g -O0 -DDEBUG
PREFIX=/usr/local

all:	test asabin asash asamock.py ifconfig-loopbacks Makefile

asabin:	asabin.c Makefile
	$(CC) $(CFLAGS) asabin.c -o asabin

bin/asabin:	asabin.c Makefile
	mkdir -p bin
	$(CC) $(CFLAGSO) asabin.c -o bin/asabin
	strip bin/asabin

install:	bin/asabin asash Makefile
	install -m 755 bin/asabin "$(PREFIX)/bin"
	install -m 755 asash "$(PREFIX)/bin"
	install -m 755 asamock.py "$(PREFIX)/bin"
	install -m 755 ifconfig-loopbacks "$(PREFIX)/bin"

commit:	test install clean Makefile
	git commit --all
	git push

clean:
	rm -f asabin asabin.o
	rm -rf asabin.dSYM bin

# Tests don't work unless it's fully installed.
test:	./asabin-test.sh ./ifconfig-loopbacks-test.sh ifconfig-loopbacks asabin bin/asabin Makefile ./asamock.py install
	echo enable | ./asabin-test.sh asabin
	echo enable | ./asabin-test.sh bin/asabin
	./ifconfig-loopbacks-test.sh ifconfig-loopbacks
#	./asamock.py

$(DEBUG).SILENT:	test
