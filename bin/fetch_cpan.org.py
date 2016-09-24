#!/usr/bin/python

import gzip
import json
import re
import urllib
import yaml

# TODO: convert this to perl for the lulz

with open('etc/pkgmon.yml', 'r') as f:
    CONFIG = yaml.load(f)

#urllib.urlretrieve('http://www.cpan.org/modules/02packages.details.txt.gz', '%s/cpan.txt.gz' % CONFIG['cache_dir'])
with gzip.open('%s/cpan.txt.gz' % CONFIG['cache_dir'], 'rb') as f:
    cpan_raw = f.read()

packages = {}
count = 0
for line in cpan_raw.split('\n'):
    count += 1
    if count <= 9:
        continue
    pkg = line.split('/')[-1].split('-')
    pkg_name = '-'.join(pkg[0:-1])
    pkg_version = pkg[-1].replace('.tar.gz', '').strip()
    try:
        packages[pkg_name].append(pkg_version)
    except KeyError:
        packages[pkg_name] = [pkg_version]
del packages['']
for package, versions in packages.iteritems():
    packages[package] = max(versions)
packages_json = json.dumps(packages, sort_keys=True, indent=4)
with open('%s/cpan.org.json' % CONFIG['cache_dir'], 'w') as f:
    f.write(packages_json)
