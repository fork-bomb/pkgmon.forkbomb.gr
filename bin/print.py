#!/usr/bin/python

import json
import yaml


def print_selected_results(config_packages):
    for project in sorted(config_packages):
        for package in config_packages[project]:
            if isinstance(package, basestring):
                pkg = package
            else:
                pkg = package.keys()[0]
            print(RESULT_TMPL.format(
                results[pkg]['rpm_project'],
                pkg,
                results[pkg]['upstream_version'],
                results[pkg]['rpm_devel_version'],
                results[pkg]['rpm_factory_version'],
                results[pkg]['rpm_leap422_version'],
                results[pkg]['rpm_leap421_version'], separ='|'))


def print_all_results():
    for package in results.keys():
        print(RESULT_TMPL.format(
            results[package]['rpm_project'],
            package,
            results[package]['upstream_version'],
            results[package]['rpm_devel_version'],
            results[package]['rpm_factory_version'],
            results[package]['rpm_leap422_version'],
            results[package]['rpm_leap421_version'], separ='|'))

with open('etc/pkgmon.yml', 'r') as f:
    CONFIG = yaml.load(f)

# TODO: make the path of the results.json (so that it can be from the web even)
with open('%s/results.json' % CONFIG['cache_dir'], 'r') as f:
    results = json.load(f)

RESULT_TMPL = '{:^32} {separ} {:^37} {separ} {:^12} {separ} {:^12} {separ} {:^12} {separ} {:^12} {separ} {:^12}'

print(RESULT_TMPL.format(
    'PROJECT',
    'PACKAGE',
    'UPSTREAM',
    'DEVEL',
    'FACTORY',
    'LEAP 42.2',
    'LEAP 42.1', separ='|'))
print(RESULT_TMPL.format('', '', '', '', '', '', '', separ='+').replace(' ', '-'))

# TODO: print only one package, or a comma-separated list of packages
# TODO: colors
# TODO: sorting if possible (configurable, via project or package)
# TODO: argument to select which of those two functions to use
print_selected_results(CONFIG['packages'])
#print_all_results()
