# mockdevices/Makefile

CC=clang
CFLAGSO=-O4 -Oz -Ofast -DNDEBUG
CFLAGS=-g -O0 -DDEBUG
PREFIX=/usr/local

all:	asabin asabin2 asabin214_0_0_1 asash asash2 asamock.py asamock2.py ifconfig-loopbacks Makefile

asabin:	asabin.c Makefile
	$(CC) $(CFLAGS) asabin.c -o asabin

asabin2: asabin2.c Makefile
	$(CC) $(CFLAGS) asabin2.c -o asabin2

asabin214_0_0_1:	asabin214_0_0_1.c Makefile
	$(CC) $(CFLAGS) asabin214_0_0_1.c -o asabin214_0_0_1

bin/asabin2:	asabin2.c Makefile
	mkdir -p bin
	$(CC) $(CFLAGSO) asabin2.c -o bin/asabin2
	strip bin/asabin2

bin/asabin:	asabin.c Makefile
	mkdir -p bin
	$(CC) $(CFLAGSO) asabin.c -o bin/asabin
	strip bin/asabin

bin/asabin214_0_0_1:	asabin214_0_0_1.c Makefile
	mkdir -p bin
	$(CC) $(CFLAGSO) asabin214_0_0_1.c -o bin/asabin214_0_0_1
	strip bin/asabin214_0_0_1

uninstall:
	rm -f "$(PREFIX)/bin/asabin"
	rm -f "$(PREFIX)/bin/asabin2"
	rm -f "$(PREFIX)/bin/asabin214_0_0_1"
	rm -f "$(PREFIX)/bin/asash"
	rm -f "$(PREFIX)/bin/asash2"
	rm -f "$(PREFIX)/bin/asamock.py"
	rm -f "$(PREFIX)/bin/asamock2.py"
	rm -f "$(PREFIX)/bin/ifconfig-loopbacks"
	rm -f /opt/local/bin/asabin
	rm -f /opt/local/bin/asabin2
	rm -f /opt/local/bin/asabin214_0_0_1
	rm -f /opt/local/bin/asash
	rm -f /opt/local/bin/asash2
	rm -f /opt/local/bin/asamock.py
	rm -f /opt/local/bin/asamock2.py
	./install-shells.sh --uninstall /usr/local/bin/asabin
	./install-shells.sh --uninstall /usr/local/bin/asabin2

install:	bin/asabin bin/asabin2 bin/asabin214_0_0_1 asash asash2 asamock.py asamock2.py Makefile
	mkdir -p "$(PREFIX)/bin"
	install -m 755 bin/asabin "$(PREFIX)/bin"
	install -m 755 bin/asabin2 "$(PREFIX)/bin"
	install -m 755 bin/asabin214_0_0_1 "$(PREFIX)/bin"
	install -m 755 asash "$(PREFIX)/bin"
	install -m 755 asash2 "$(PREFIX)/bin"
#	install -m 755 asamock.py "$(PREFIX)/bin"
#	ln -sf /Users/*/Documents/src/mockdevices/asamock.py /usr/local/bin/asamock.py
	ln -sf /usr/local/src/mockdevices/asamock.py /usr/local/bin/asamock.py
	ln -sf /usr/local/src/mockdevices/asamock2.py /usr/local/bin/asamock2.py
	install -m 755 ifconfig-loopbacks "$(PREFIX)/bin"
	mkdir -p /opt/local/bin
	ln -sf ../../../usr/local/bin/asabin /opt/local/bin/asabin
	ln -sf ../../../usr/local/bin/asabin2 /opt/local/bin/asabin2
	ln -sf ../../../usr/local/bin/asabin214_0_0_1 /opt/local/bin/asabin214_0_0_1
#	ln -sf ../../../usr/local/bin/asamock.py /opt/local/bin/asamock.py
#	ln -sf /Users/*/Documents/src/mockdevices/asamock.py /opt/local/bin/asamock.py
	ln -sf /usr/local/src/mockdevices/asamock.py /opt/local/bin/asamock.py
	ln -sf ../../../usr/local/bin/asash /opt/local/bin/asash
	ln -sf ../../../usr/local/bin/asash2 /opt/local/bin/asash2
	./install-shells.sh /usr/local/bin/asabin
	./install-shells.sh /usr/local/bin/asabin2

commit:	test install clean Makefile
	git commit --all
	git push

clean:
	rm -f asabin asabin.o asabin2 asabin2.o asabin214_0_0_1 asabin214_0_0_1.o
	rm -rf asabin.dSYM bin asabin2.dSYM asabin214_0_0_1.dSYM

# Tests don't work unless it's fully installed.
test:	./asabin-test.sh ./ifconfig-loopbacks-test.sh ifconfig-loopbacks asabin bin/asabin Makefile ./asamock.py install
	true
#	echo enable | ./asabin-test.sh asabin
#	echo enable | ./asabin-test.sh bin/asabin
#	./test_ifconfig-loopbacks.sh ifconfig-loopbacks
#	./asamock.py

$(DEBUG).SILENT:	test
