#!/usr/bin/env python3

from interactive_asa import ASA

a = ASA('test_asa.conf')

a.send('enable')
a.send('config t')
print(a.send('access-list nate extended permit ip 10.0.0.0 255.0.0.0 any'))
print(a.send('access-list nate line 1 extended permit ip 10.0.0.1 255.0.0.255 any'))
print(a.send('access-list nate line 2 extended permit ip 10.0.0.2 255.0.0.255 any'))
print(a.send('access-list nate line 1 extended permit ip 10.0.0.3 255.0.0.255 any'))
