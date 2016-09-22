#!/usr/bin/python

import json
import osc.conf
import osc.core
import xml.etree.ElementTree as ET
import yaml


def get_projects(CONFIG):
    return CONFIG['products'] + CONFIG['packages'].keys()


def osc_api(project):
    apiurl = osc.conf.config['apiurl']
    if project.endswith(':Update'):
        url = osc.core.makeurl(apiurl, ['published', project, 'standard', 'src'])
    else:
        url = osc.core.makeurl(apiurl, ['status', 'project', project])
    return osc.core.http_GET(url).read()

osc.conf.get_config()

with open('etc/pkgmon.yml', 'r') as f:
    CONFIG = yaml.load(f)

PROJECTS = get_projects(CONFIG)

# TODO: argument to fetch and write only new projects
for project in PROJECTS:
    # fetch and write the full project XML output
    project_xml_raw = osc_api(project)
    with open('%s/%s.xml' % (CONFIG['cache_dir'], project), 'w') as f:
        f.write(project_xml_raw)

    # parse and write a JSON for the project's packages
    project_xml = ET.fromstring(project_xml_raw)
    packages_dict = {}
    if project.endswith(':Update'):
        packages = project_xml.findall('entry')
        for package in packages:
            pkg = package.get('name').split('-')
            packages_dict['-'.join(pkg[:-2])] = pkg[-2]
    else:
        packages = project_xml.findall('package')
        for package in packages:
            packages_dict[package.get('name')] = package.get('version')
    packages_json = json.dumps(packages_dict, sort_keys=True, indent=4)
    with open('%s/%s.json' % (CONFIG['cache_dir'], project), 'w') as f:
        f.write(packages_json)
