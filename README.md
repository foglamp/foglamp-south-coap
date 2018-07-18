# foglamp-south-coap

FogLAMP South Plugin for CoAP

### Packaging for CoAP South
This repo contains the scripts used to create a foglamp-south-coap package.

#### The make_deb script
```
$ ./make_deb help

 make_deb help {x86|arm} [clean|cleanall]
This script is used to create the Debian package of foglamp south coap
Arguments:
 help     - Display this help text
 x86      - Build an x86_64 package
 arm      - Build an armhf package
 clean    - Remove all the old versions saved in format .XXXX
 cleanall - Remove all the versions, including the last one
$
```

#### Building a Package

Select the architecture to use, *x86* or *arm*.
Finally, run the ``make_deb`` command:

```
$ ./make_deb x86
The package root directory is         : /home/foglamp/foglamp-south-coap
The FogLAMP south coap version is     : 1.0.0
The package will be built in          : /home/foglamp/foglamp-south-coap/packages/Debian/build
The architecture is set as            : x86_64
The package name is                   : foglamp-south-coap-1.0.0-x86_64

Populating the package and updating version file...Done.
Building the new package...
dpkg-deb: building package 'foglamp-south-coap' in 'foglamp-south-coap-1.0.0-x86_64.deb'.
Building Complete.
$
```

The result will be:

```
$ ls -l packages/Debian/build/
total 12
drwxrwxr-x 4 foglamp foglamp 4096 Jul 11 16:24 foglamp-south-coap-1.0.0-x86_64
-rw-r--r-- 1 foglamp foglamp 4574 Jul 11 16:24 foglamp-south-coap-1.0.0-x86_64.deb
$
```

If you execute the ``make_deb`` command again, you will see:

```
$ ./make_deb x86
The package root directory is         : /home/foglamp/foglamp-south-coap
The FogLAMP south coap version is     : 1.0.0
The package will be built in          : /home/foglamp/foglamp-south-coap/packages/Debian/build
The architecture is set as            : x86_64
The package name is                   : foglamp-south-coap-1.0.0-x86_64

Saving the old working environment as foglamp-south-coap-1.0.0-x86_64.0001
Populating the package and updating version file...Done.
Saving the old package as foglamp-south-coap-1.0.0-x86_64.deb.0001
Building the new package...
dpkg-deb: building package 'foglamp-south-coap' in 'foglamp-south-coap-1.0.0-x86_64.deb'.
Building Complete.
$
```

```
$ ls -l packages/Debian/build/
total 24
drwxrwxr-x 4 foglamp foglamp 4096 Jul 11 16:26 foglamp-south-coap-1.0.0-x86_64
drwxrwxr-x 4 foglamp foglamp 4096 Jul 11 16:24 foglamp-south-coap-1.0.0-x86_64.0001
-rw-r--r-- 1 foglamp foglamp 4576 Jul 11 16:26 foglamp-south-coap-1.0.0-x86_64.deb
-rw-r--r-- 1 foglamp foglamp 4574 Jul 11 16:24 foglamp-south-coap-1.0.0-x86_64.deb.0001
$
```

... where the previous build is now marked with the suffix *.0001*.


#### Cleaning the Package Folder

Use the ``clean`` option to remove all the old packages and the files used to make the package.
Use the ``cleanall`` option to remove all the packages and the files used to make the package.

#### Manual installation
If you wish to manually install this plugin you will require two Python packages to be installed
```
sudo pip3 install --upgrade "aiocoap[all]"
sudo pip3 install cbor2
```

