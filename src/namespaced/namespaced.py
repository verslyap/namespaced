#!/usr/bin/env python
"""
    This file is part of namespaced.

    namespaced is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    namespaced is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with namespaced.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys
import dbus, dbus.service, dbus.exceptions
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import signal
import NSManager
import argparse
import yaml
import logging

NSList = None

def parse():
    parser = argparse.ArgumentParser("namespaced",description="bind mounts linux kernel namespaces from either a configuration file or a dbus interface")
    parser.add_argument("--configurationfile",default="/etc/namespaced/namespaced.yaml",help="the absolute path to the configuration file. defaults to /etc/namespaced/namespaced.yaml if omitted")
    parser.add_argument("--namespacedirectory",default="/run/namespace/",help="the absolute path to the directory where kernel namespaces are bind mounted. defaults to /run/namespace if omitted")
    parser.add_argument("--loglocation",help="the location that the log file is written to. defaults to the same directory as the executable if omitted")
    #parser.add_argument("--logverbosity",help="an integer (1 through 5) representing the verbosity of messages written to the log file. currently, only the info level is logged and this argument is ignored")

    return parser.parse_args()

def shutdown(signal,frame):
    global NSList
    NSList.removeall()
    logging.info("namespaces removed")
    if os.path.exists(o.namespacedirectory):
        os.rmdir(o.namespacedirectory)
    logging.info(f"{o.namespacedirectory} deleted")
    logging.info("namespaced terminating. . .")
    logging.shutdown()
    sys.exit(0)


def main():
    global NSList
    logging.info("namespaced started!")
    if not os.path.exists(o.namespacedirectory):
        os.makedirs(o.namespacedirectory)
    logging.info(f"created {o.namespacedirectory}")
    DBusGMainLoop(set_as_default=True)
    loop = GLib.MainLoop()
    bus_name = dbus.service.BusName("org.apv.namespaced",bus=dbus.SystemBus(),do_not_queue=True)
    NSList = NSManager.NSManager(bus_name)
    f = open(o.configurationfile,"r")
    NSList.load(yaml.safe_load(f))
    logging.info(f"configuration from {o.configurationfile}")
    signal.signal(signal.SIGTERM,shutdown)
    loop.run()

o = parse()
logging.basicConfig(filename=o.loglocation, encoding='utf-8', level=logging.INFO)

if __name__ == "__main__":
    main()