#!/usr/bin/env python3

from interactive_asa import ASA
from asa_config import asa_config

c = asa_config()

a = ASA(configstr=c)
print(a.send('show access-list outside-in'))
