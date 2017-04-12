# mockdevices/Makefile

CC=cc
CFLAGSO=-O4 -Oz -Ofast -DNDEBUG
CFLAGS=-g -O0 -DDEBUG
PREFIX=/usr/local

all:	asabin asash asamock.py ifconfig-loopbacks Makefile

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
	rm -f "$(PREFIX)/bin/ifconfig-loopbacks"
	rm -f /opt/local/bin/asabin
	rm -f /opt/local/bin/asash
	rm -f /opt/local/bin/asamock.py

install:	bin/asabin asash Makefile
	mkdir -p "$(PREFIX)/bin"
	install -m 755 bin/asabin "$(PREFIX)/bin"
	install -m 755 asash "$(PREFIX)/bin"
#	install -m 755 asamock.py "$(PREFIX)/bin"
	ln -sf /Users/*/Documents/src/mockdevices/asamock.py /usr/local/bin/asamock.py
	install -m 755 ifconfig-loopbacks "$(PREFIX)/bin"
	mkdir -p /opt/local/bin
	ln -sf ../../../usr/local/bin/asabin /opt/local/bin/asabin
#	ln -sf ../../../usr/local/bin/asamock.py /opt/local/bin/asamock.py
	ln -sf /Users/*/Documents/src/mockdevices/asamock.py /opt/local/bin/asamock.py
	ln -sf ../../../usr/local/bin/asash /opt/local/bin/asash

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
#	./ifconfig-loopbacks-test.sh ifconfig-loopbacks
#	./asamock.py

$(DEBUG).SILENT:	test
