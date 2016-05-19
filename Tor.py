#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

class Tor(object):
    TOR_PATH = r'my_path_to_tor'

    def __init__(self, socket_port):
        if not os.path.exists(str(socket_port)):
            os.mkdir(str(socket_port))
        cmd = '"%s" --ignore-missing-torrc --AvoidDiskWrites 1 --SOCKSPort %s --DataDirectory %s' % (self.TOR_PATH, socket_port, socket_port)
        self.proc = subprocess.Popen(cmd, shell=False)

    def __del__(self):
        self.proc.terminate()