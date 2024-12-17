# AlmaLinux 9 and dpres-siptools dependencies

MediaJam needs dpres-siptools to be installed with certain dependencies in AlmaLinux 9 server. 
https://github.com/Digital-Preservation-Finland/dpres-siptools

Digital-Preservation-Finland has developed RPM packages to make installation easier.

> Install these as root user.

**INSTALL BASIC TOOLS**
```
dnf install git
dnf install tar
dnf install nano
```
**INSTALL RPM TOOLS**
```
rpm --import https://pas-jakelu.csc.fi/RPM-GPG-KEY-pas-support-el9 
dnf install dnf-plugins-core 
dnf config-manager --add-repo=https://pas-jakelu.csc.fi/pas-jakelu-csc-fi.repo
dnf config-manager --set-enabled crb
dnf install epel-release
dnf install --nogpgcheck https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm
```
**INSTALL DPRES TOOLS**
```
dnf install python3-file-scraper-full 
dnf install python3-dpres-siptools 
```

