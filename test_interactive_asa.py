#!/usr/bin/env python3

from interactive_asa import ASA

a = ASA('asa.conf')
print(a.show_object_group('MPI_SERVICES'))
print(a.show_access_list('outside-in'))


