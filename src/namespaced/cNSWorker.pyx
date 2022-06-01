# cython: language_level=3
# cython: c_string_type=unicode
# cython: c_string_encoding=ascii
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
from pathlib import Path

cdef extern from "<unistd.h>":
    int getpid()

cdef extern from "<errno.h>":
    int errno

cdef extern from "<sys/ioctl.h>":
    int ioctl(int fd, unsigned int request)

cdef extern from "<sys/mount.h>":
    int mount(char* source, char* target, char* filesystemtype, unsigned long mountflags, data)
    int umount(char* target)
    int MS_BIND

cdef extern from "<asm-generic/ioctl.h>":
    int _IO(int type, int nr)

cdef extern from "<sched.h>":
    int unshare(int flags)
    int CLONE_NEWCGROUP
    int CLONE_NEWIPC
    int CLONE_NEWNET
    int CLONE_NEWNS
    int CLONE_NEWPID
    #int CLONE_NEWTIME
    int CLONE_NEWUSER
    int CLONE_NEWUTS

NSIO = 0xb7
NS_GET_NSTYPE = _IO(NSIO,0x3)
CLONE_NEWTIME = 0x00000080

cpdef str getNamespaceType(str name, str path):
    src = path + "/" + name
    fd = open(src)
    ret = ioctl(fd.fileno(),NS_GET_NSTYPE)
    return NSIntToString(ret)

# Error codes:
# -1: Could not create mountpoint
# -2: Mount failed
cpdef int makeNamespace(str t,str name,str path):
    cdef:
        str asdf = ""
        char* empty = asdf
        char* t1 = t
    src = "/proc/" + f"{getpid()}" + "/ns/" + t
    cdef char* s = src
    dest = path + "/" + name
    cdef char* d = dest
    p = Path(dest)
    try:
        p.touch()
    except FileExistsError:
        return -1
    unshare(NSStringToInt(t1))
    x = mount(s,d,empty,MS_BIND,empty)
    if x < 0:
        return -2
    return open(p).fileno()

# Error codes:
# -1: Could not remove mountpoint after sucessful unmount
# -2: Could not unmount Namespace
cpdef int removeNamespace(str name, str path):
    p = path + "/" + name
    cdef int i = umount(p)
    if i == -1:
        return -1
    try:
        Path(p).unlink()
    except FileNotFoundError:
        return -2
    return 0

cdef str NSIntToString(int type):
    if (type == CLONE_NEWCGROUP):
        return "cgroup"
    elif (type == CLONE_NEWIPC):
        return "ipc"
    elif (type == CLONE_NEWNET):
        return "net"
    elif (type == CLONE_NEWNS):
        return "mount"
    elif (type == CLONE_NEWPID):
        return "pid"
    elif (type == CLONE_NEWTIME):
        return "time"
    elif (type == CLONE_NEWUSER):
        return "user"
    elif (type == CLONE_NEWUTS):
        return "uts"
    else:
        return "error"

cdef int NSStringToInt( type):
    if (type == "cgroup"):
        return CLONE_NEWCGROUP
    elif (type == "ipc"):
        return CLONE_NEWIPC
    elif (type == "net"):
        return CLONE_NEWNET
    elif (type == "mount"):
        return CLONE_NEWNS
    elif (type == "pid"):
        return CLONE_NEWPID
    elif (type == "time"):
        return CLONE_NEWTIME
    elif (type == "user"):
        return CLONE_NEWUSER
    elif (type == "uts"):
        return CLONE_NEWUTS
    else:
        return -1