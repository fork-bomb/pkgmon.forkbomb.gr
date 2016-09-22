#!/usr/bin/ruby

require 'open-uri'
require 'net/http'
require 'json'
require 'yaml'

CONFIG = 'etc/pkgmon.yml'

if (File.exists?(CONFIG))
  $config = YAML.load_file(CONFIG)
else
  raise "Configuration file #{CONFIG} does not exist"
end

f = open('https://rubygems.org/specs.4.8.gz')
m = Marshal.load(Gem.gunzip(f.read))
f.close

gems = Hash.new
m.each do |g|
  if g[2] == 'ruby'
    #gems[g[0]] ||= Array.new
    #gems[g[0]] << g[1]
    gems[g[0]] = g[1]
  end
end

open("#{$config['cache_dir']}/rubygems.org.json", 'w') do |f|
  f.write(JSON.pretty_generate(gems))
end
