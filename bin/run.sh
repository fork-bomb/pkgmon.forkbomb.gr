#!/bin/sh

# TODO: parse the pkgmon.yml

bin/fetch_cpan.org.py
bin/fetch_pypi.python.org.py
bin/fetch_rubygems.org.rb
bin/fetch_osc.py
bin/create_results.py
# TODO: unhardcode this
cp tmp/cache/results.json /home/tampakrap/public_html
