#!/usr/bin/python

import json
import urllib2
import yaml

# TODO: convert this to perl for the lulz

with open('etc/pkgmon.yml', 'r') as f:
    CONFIG = yaml.load(f)

cpan_raw = urllib2.urlopen('http://www.cpan.org/modules/02packages.details.txt.gz')

packages = {}
for line in cpan_raw:
    pkg = line.split('/')[-1].split('-')
    packages['-'.join(pkg[0:-1])] = pkg[-1].replace('.tar.gz', '').strip()
packages_json = json.dumps(packages, sort_keys=True, indent=4)
with open('%s/cpan.org.json' % CONFIG['cache_dir'], 'w') as f:
    f.write(packages_json)
