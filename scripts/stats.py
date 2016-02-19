#
# Prints statistics about the API misuses in the entire dataset.
#
from __future__ import division
import os
import yaml
from sets import Set

rootpath = ".."
datapath = os.path.join(rootpath, "data")

print "Scanning misuses..."

number_of_misuses = 0
number_of_crashes = 0
projects = Set()
sources = Set()

for filename in os.listdir(datapath):
    if filename.endswith(".yml"):
        filename = os.path.join(datapath, filename)
        file = open(filename, 'r')
        try:
            misuse = yaml.load(file)

            number_of_misuses += 1
            if misuse["crash"]:
                number_of_crashes += 1

            sources.add(misuse["source"]["name"])
            if "project" in misuse:
                projects.add(misuse["project"]["name"])
            else:
                projects.add("survey")
        
        except KeyError as e:
            print "Did not find '%s' in '%s'" % (e.args[0], filename)
        finally:
            file.close()

print
print "MUBench contains:"
print "- %d misuses" % number_of_misuses
print "- %d crashes (%.1f%%)" % (number_of_crashes, (number_of_crashes / number_of_misuses * 100))
print "- %d sources" % len(sources)
print "- %d projects" % len(projects)
