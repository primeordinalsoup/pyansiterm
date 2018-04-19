# pyansiterm
This is a module for driving ANSI terminals.  It gives access to python to print colour text, bold etc and also provides basic widgets to allow doing very simple outputs.

## Installing
From the Dynamic repo:
```bash
sudo apt-get install pyansiterm
```
*this should be already installed as part of standard dev. meta package.*

Via setuptools:
```bash
sudo python3 setup.py install          #installs to site-packages
sudo python3 setup.py install develop  #installs in place so changes to source apply instantly
```

Via Pip manually, in a python 3 environment:
```bash
pip install -r requirements.txt
pip install -e .
```

Packaging
---------
You can make a debian package directly from this repo.  In the
following example the maintainer is the debian package maintainer, and the
version is the package version.
```bash
sudo apt-get install checkinstall
sudo checkinstall --exclude=/usr/local/lib/python3.5/dist-packages/easy-install.pth --pkgversion=1.0.0 --pkglicense=DCL --maintainer='pkraak@dynamiccontrols.com' -y python3 setup.py install
```

Usage
-----
See tests for examples of use.

