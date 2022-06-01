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

import pyximport
pyximport.install()
import os
import dbus
import cNSWorker
import namespaced
from enum import Enum
import logging

class result(Enum):
    NOTMOUNTPOINT = 1
    NOTNAMESPACE = 2
    NAMEPSACETYPEMISMATCH = 3
    FILEEXISTS = 4
    NAMESPACEDOESNOTEXIST = 5
    OKAY = 6

class NamespaceException(Exception):
    pass

def isnamespace(name):
    if not os.path.ismount(namespaced.o.namespacedirectory + "/" + name):
        return result.NOTMOUNTPOINT
    if cNSWorker.getNamespaceType(name,namespaced.o.namespacedirectory) == "error":
        return result.NOTNAMESPACE
    return result.OK

def isnamespacematch(name,namespace):
    if cNSWorker.getNamespaceType(name,namespaced.o.namespacedirectory) == namespace:
        return True
    else:
        return False

class namespace:
    def __init__(self,type,name):
        if isinstance(name,dbus.String):
            self.name = str(name)
        else:
            self.name = name
        if isinstance(type,dbus.String):
            self.type = str(type)
        else:
            self.type = type
        r = cNSWorker.makeNamespace(self.type,self.name,namespaced.o.namespacedirectory)
        if r < 0:
            raise NamespaceException
            return r

    def __eq__(self,operand):
        if isinstance(operand,str):
            if self.name == operand:
                return True
        elif namespaced.o.namespacedirectory == operand.path and self.name == operand.name and self.type == operand.type:
            return True
        else:
            return False

    def __del__(self):
        r = cNSWorker.removeNamespace(self.name,namespaced.o.namespacedirectory)
        if r < 0:
            raise NamespaceException
            return r