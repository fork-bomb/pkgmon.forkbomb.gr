#!/usr/bin/python

from pkg_resources import parse_version as V
import json
import urllib2
import yaml


class Package:
    rpm_name = None
    rpm_project = None
    rpm_devel_version = None
    rpm_factory_version = None
    rpm_leap421_version = None
    rpm_leap422_version = None
    upstream_name = None
    upstream_service = None
    upstream_version = None
    upstream_repo_owner = None

    def __init__(self, rpm_name, rpm_project, upstream_data={}):
        self.rpm_name = rpm_name
        self.rpm_project = rpm_project
        self.rpm_devel_version = self._get_rpm_devel_version()
        self.rpm_factory_version = self._get_rpm_factory_version()
        self.rpm_leap421_version = self._get_rpm_leap421_version()
        self.rpm_leap422_version = self._get_rpm_leap422_version()
        self.upstream_name = self._get_upstream_name(upstream_data)
        self.upstream_service = self._get_upstream_service(upstream_data)
        self.upstream_version = self._get_upstream_version(upstream_data)

    def _get_rpm_devel_version(self):
        return cache_json_files[self.rpm_project][self.rpm_name]

    def _get_rpm_factory_version(self):
        try:
            return cache_json_files['openSUSE:Factory'][self.rpm_name]
        except:
            return ''

    def _get_rpm_leap421_version(self):
        try:
            return cache_json_files['openSUSE:Leap:42.1:Update'][self.rpm_name]
        except KeyError:
            try:
                return cache_json_files['openSUSE:Leap:42.1'][self.rpm_name]
            except KeyError:
                return ''

    def _get_rpm_leap422_version(self):
        try:
            return cache_json_files['openSUSE:Leap:42.2'][self.rpm_name]
        except KeyError:
            return ''

    def _get_upstream_name(self, upstream_data):
        try:
            upstream_name = upstream_data['name']
        except KeyError:
            upstream_name = self.rpm_name

        return upstream_name.replace('rubygem-', '').replace('python-', '').replace('perl-', '')

    def _get_upstream_service(self, upstream_data):
        try:
            return upstream_data['service']
        except KeyError:
            if self.rpm_name.startswith('rubygem-'):
                return 'rubygems.org'
            elif self.rpm_name.startswith('python-'):
                return 'pypi.python.org'
            elif self.rpm_name.startswith('perl-'):
                return 'cpan.org'
            else:
                return 'ERROR'

    def _get_upstream_repo_owner(self, upstream_data):
        return upstream_data['owner']

    def _get_upstream_version(self, upstream_data):
        # TODO: implement higher_version
        def get_max_version(versions_list):
            curr_max = versions_list[0]
            for version in versions_list:
                if V(version) > V(curr_max):
                    curr_max = version
            return curr_max

        def get_github_gitlab_max_version(full_api):
            all_tags = []
            for part_api in full_api:
                all_tags.append(part_api['name'].replace('release-', '').strip('v'))
            return get_max_version(all_tags)

        if self.upstream_service in ALL_CACHED_SERVICES:
            return cache_json_files[self.upstream_service][self.upstream_name]
        elif self.upstream_service in CONFIG['social_vcs']:
            self.upstream_repo_owner = self._get_upstream_repo_owner(upstream_data)
            if self.upstream_service == 'github.com':
                raw = urllib2.urlopen('https://api.%s/repos/%s/%s/tags' % (self.upstream_service, self.upstream_repo_owner, self.upstream_name))
                return get_github_gitlab_max_version(json.loads(raw.read()))
            elif self.upstream_service == 'gitlab.com':
                req = urllib2.Request('https://%s/api/v3/projects/%s%%2F%s/repository/tags' % (self.upstream_service, self.upstream_repo_owner, self.upstream_name))
                req.add_header('PRIVATE-TOKEN', CONFIG['gitlab_token'])
                up_res = urllib2.urlopen(req)
                return get_github_gitlab_max_version(json.loads(up_res.read()))
        else:
            return 'ERROR'

    def create_dict_entry(self):
        return {
            'rpm_project': self.rpm_project,
            'rpm_devel_version': self.rpm_devel_version,
            'rpm_factory_version': self.rpm_factory_version,
            'rpm_leap421_version': self.rpm_leap421_version,
            'rpm_leap422_version': self.rpm_leap422_version,
            'upstream_name': self.upstream_name,
            'upstream_version': self.upstream_version,
            'upstream_service': self.upstream_service,
            'upstream_repo_owner': self.upstream_repo_owner,
        }


def get_cache_files(CONFIG):
    cache_files = CONFIG['products'] + PACKAGES.keys() + ALL_CACHED_SERVICES
    cache_json_files = {}
    for cache_file in cache_files:
        with open('%s/%s.json' % (CONFIG['cache_dir'], cache_file)) as f:
            cache_json_files[cache_file] = json.load(f)
    return cache_json_files

with open('etc/pkgmon.yml', 'r') as f:
    CONFIG = yaml.load(f)

PACKAGES = CONFIG['packages']
ALL_CACHED_SERVICES = CONFIG['cached_services'] #+ CONFIG['cached_listindex_services']
cache_json_files = get_cache_files(CONFIG)

# TODO: write each Package in separate json and then combine them (so that we
#       don't lose the previously created result in failure of one package)
results = {}
for project, packages in PACKAGES.iteritems():
    for package in packages:
        if isinstance(package, basestring):
            pkg_name = package
            try:
                pkg = Package(package, project)
            except Exception, e:
                print "%s: %s" % (pkg_name, e)
        else:
            pkg_name, pkg_data = package.items()[0]
            try:
                pkg = Package(pkg_name, project, pkg_data)
            except Exception, e:
                print "%s: %s" % (pkg_name, e)
        results[pkg.rpm_name] = pkg.create_dict_entry()

results_json = json.dumps(results, sort_keys=True, indent=4)
with open('%s/results.json' % CONFIG['cache_dir'], 'w') as f:
    f.write(results_json)
