#!/usr/bin/env python3

from interactive_asa import ASA

a = ASA('test_asa.conf')
print(a.show_access_list('cra'))
