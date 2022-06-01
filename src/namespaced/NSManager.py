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

from types import new_class
import namespace
import yaml
import os
import dbus.service
import logging
import namespaced

import pyximport
pyximport.install()
import cNSWorker

class NSManager(dbus.service.Object):
    """Maintains a list of managed linux kernel namespaces in the designated folder (/run/namespace/ by default)"""

    def __init__(self,bus_name):
        self.namespaces = []
        super().__init__(bus_name,"/org/apv/namespaced/namespaces")
        logging.info("connected to system bus")

    def __contains__(self,NS):
        for i in self.list:
            if i == NS:
                return True
        return False

    @dbus.service.method("org.apv.namespaced.namespaces.add",in_signature='ss', out_signature='i')
    def add(self,name,type):
        """creates a kernel namespace of the given type bind mounted to a file with the given name under /run/namespace/"""
        if not os.path.exists("/run/namespace/" + name):
            ns = namespace.namespace(type,name)
            self.namespaces.append(ns)
            logging.info(f"namespace {name} of type {type} created at /run/namespace")
            return namespace.result.OKAY.value
        else:
            return namespace.result.FILEEXISTS.value

    @dbus.service.method("org.apv.namespaced.namespaces.remove",in_signature='s', out_signature='i')
    def remove(self,name):
        """removes the bind mounted kernel namespace of the given name under /run/namespace/"""
        if os.path.exists("/run/namespace/" + name):
            self.namespaces.remove(name)
            logging.info(f"removed namespace {name}")
            return namespace.result.OKAY.value
        else:
            return namespace.result.NAMESPACEDOESNOTEXIST.value

    def removeall(self):
            self.namespaces.clear()

    def load(self,config):
        for i in config:
            self.add(i,config[i]['namespace'])

    @dbus.service.method("org.apv.namespaced.namespaces.reload",in_signature=None, out_signature=None)
    def reload(self):
        """reloads the config file specified by the --configurationfile flag.  Any added namespaces under /run/namespace will be removed.  Any namespaced present in the config but since removed from /run/namespace/ will be created.  If a namespace of the same name but a different type exists in /run/namespace, it will be removed and recreated to match the config file"""
        logging.info("reloading namespaces from configuration")
        config = yaml.safe_load(namespaced.o.configurationfile)
        for i in os.scandir("/run/namespace/"):
            #1: Remove any files that are not namespaces
            if namespace.isnamespace(i.path) == namespace.result.NOTMOUNTPOINT:
                os.remove(i.path)
                continue
            #2: Check to see if entry is in config (and is same namespace type)
            filename = os.path.basename(i.path)
            found = False
            for n in config:
                if n == filename:
                    found = True
            #       -> if name matches but different type than config, delete and recreate
                    if not namespace.isnamespacematch(i.path,n,config[n]):
                        self.remove(n)
                        self.add(n,config[n]['namespace'])
            #    -> if namespace name and type match config, skip over it
                    else:
                        continue
                    # -> the namespace has been found, there is no need to search the rest of the list
                    if found:
                        break
            # -> if name does *not* is not in the config, delete the namespace
            if not found:
                self.remove(filename)
            #3: Check to see if there are any namespaces in the list
        for i in config:
            if not os.path.exists("/run/namespace/" + i):
                # -> create namespace
                self.add(i,config[i]['namespace'])
        logging.info("configuration reloaded")
        return self.dump()

    @dbus.service.method("org.apv.namespaced.namespaces.dump",in_signature=None, out_signature=None)
    def dump(self):
        """returns a yaml snippet describing the current namespaces present at /run/namespace/"""
        logging.info("dump requested")
        t = {}
        for i in self.namespaces:
            t[i.name] = {}
            t[i.name]['namespace'] = i.type
        return yaml.dump(t)