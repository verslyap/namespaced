namespaced -- provides bind mounted linux kernel namespaces from either a configuration file or dbus interface

====

## SYNOPSIS
'namespaced' [OPTIONS]

## DESCRIPTION

namespaced reads a configuration file at startup which describes a series of linux kernel namespaces to be bind mounted at a particular location.

namespaced also provides a dbus interface to any client connecting to org.apv.namespaced

## ARGUEMENTS

--configfile
the location of the configuration file to uses.  if omitted, it defaults to /etc/namespaced/namespaced.yaml

--namespacelocation
the location to place place created namespaces. if omitted it defaults to /run/namespace

--loglocation
the location of the log file. if omitted it defaults to the same location as the executable

## CONFIGURATION

the namespaced configuration is a series of yaml key/value pairs, where the key is the name of the file that a namespace will be bind mounted into inside the location specified in the --namespacelocation directory.  The value associated with this key is itself a nested key/value pair.  The subkey's name must be 'namespace' and the value must be one of the supported namespace types listed in XXXXXXXXXX.  See example section below for more.

## DBUS API

add(type,name)
creates a kernel namespace of the given type bind mounted to a file with the given name under /run/namespace/

remove(name)
removes the bind mounted kernel namespace of the given name under /run/namespace/

reload()
reloads the config file specified by the --configurationfile flag.  Any added namespaces under /run/namespace will be removed.  Any namespaced present in the config but since removed from /run/namespace/ will be created.  If a namespace of the same name but a different type exists in /run/namespace, it will be removed and recreated to match the config file

dump()
returns a yaml snippet describing the current namespaces present at /run/namespace/

## EXAMPLES

The configruation file below demonstrates a yaml file that will create a namespace bind mount named cgrouptest of type cgroup, and a network namespace named nettest.

cgrouptest:
     type:cgroup
nettest
     type:net

by running ls on the namespace directory, we can see the namespaces have been unshared and mounted

ls -al /run/namespace
total 0
drwxr-xr-x.  2 root root  100 Nov  8 19:07 .
drwxr-xr-x. 52 root root 1340 Nov  7 20:07 ..
-r--r--r--.  1 root root    0 Nov  8 19:07 cgrouptest
-r--r--r--.  1 root root    0 Nov  8 19:07 nettest

## SEE ALSO

namespaces(7)

## COPYRIGHT

namespaced was written by Adam P Verslype.  It is licsensed under the terms of the Gnu Public Licsense v3 (GPLv3).