import unittest
import yaml
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import signal
from pathlib import Path
import NSManager

class test_reload(unittest.TestCase):

    def setUP(self):
        DBusGMainLoop(set_as_default=True)
        loop = GLib.MainLoop()
        self.nsm = NSManager.NSManager(dbus.service.BusName("org.apv.namespaced",bus=dbus.SystemBus(),do_not_queue=True))
        self.nsm.add("cgroup","xvdsaojfew")
        self.nsm.add("cgroup","cgrouptest")
        self.nsm.add("net","cgrouptest2")
        
    def test_reload(self):
        f = open(Path("/etc/namespaced/namespaced.yml"))
        self.nsm.reload(yaml.safe_load(f))

tr = test_reload()
tr.setUP()
tr.test_reload()