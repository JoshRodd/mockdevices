# mockdevices/Makefile

CC=cc
CFLAGSO=-O4 -Oz -Ofast -DNDEBUG
CFLAGS=-g -O0 -DDEBUG
PREFIX=/usr/local

all:	test asabin ifconfig-loopbacks Makefile

asabin:	asabin.c Makefile
	$(CC) $(CFLAGS) asabin.c -o asabin

bin/asabin:	asabin.c Makefile
	mkdir -p bin
	$(CC) $(CFLAGSO) asabin.c -o bin/asabin
	strip bin/asabin

install:	bin/asabin asash test Makefile
	install -m 755 bin/asabin "$(PREFIX)/bin"
	install -m 755 asash "$(PREFIX)/bin"
	install -m 755 ifconfig-loopbacks "$(PREFIX)/bin"

commit:	test clean Makefile
	git commit --all

clean:
	rm -f asabin asabin.o
	rm -rf asabin.dSYM bin

test:	./asabin-test.sh ./ifconfig-loopbacks-test.sh ifconfig-loopbacks asabin bin/asabin Makefile
	./asabin-test.sh asabin
	./asabin-test.sh bin/asabin
	./ifconfig-loopbacks-test.sh ifconfig-loopbacks

$(DEBUG).SILENT:	test
