#!/usr/bin/python

from bs4 import BeautifulSoup
import json
import urllib2
import yaml

with open('etc/pkgmon.yml', 'r') as f:
    CONFIG = yaml.load(f)

pypi_raw = urllib2.urlopen('https://pypi.python.org/pypi/?').read()
links = BeautifulSoup(pypi_raw, 'html.parser').table.find_all('a')
packages = {}
for link in links:
    split_link = link.get('href').split('/')
    packages[split_link[2]] = split_link[3]
packages_json = json.dumps(packages, sort_keys=True, indent=4)
with open('%s/pypi.python.org.json' % CONFIG['cache_dir'], 'w') as f:
    f.write(packages_json)
