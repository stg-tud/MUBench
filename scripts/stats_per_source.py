#
# Prints statistics about the API misuses per source.
#
from __future__ import division
import os
import yaml

rootpath = ".."
datapath = os.path.join(rootpath, "data")

print "Scanning misuses..."

sources = {}

filename = os.path.join(rootpath, "sources.yml")
file = open(filename, 'r')
try:
    sources = yaml.load(file)
    for source in sources:
        sources[source]["misuses"] = 0
        sources[source]["crashes"] = 0
finally:
    file.close()

for filename in os.listdir(datapath):
    if filename.endswith(".yml"):
        filename = os.path.join(datapath, filename)
        file = open(filename, 'r')
        try:
            misuse = yaml.load(file)
            
            sourcename = misuse["source"]["name"]
            source = sources[sourcename]
            source["misuses"] += 1
            if misuse["crash"]:
                source["crashes"] += 1
            sources[sourcename] = source
        except KeyError as e:
            print "Did not find '%s' in '%s'" % (e.args[0], filename)
        finally:
            file.close()

print
print "%20s %7s %9s %15s   %15s" % ("Source", "Size", "Reviewed", "Misuses", "Crashes")
for sourcename in sources:
    source = sources[sourcename]
    print "%20s %7d %9d %5d - % 6.1f%%   %5d - % 6.1f%%" % (sourcename, source["size"], source["reviewed"], source["misuses"], (source["misuses"] / source["reviewed"] * 100), source["crashes"], (source["crashes"] / source["misuses"] * 100))
