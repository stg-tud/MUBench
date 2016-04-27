#
# Prints statistics about the API misuses per project.
#
from __future__ import division
import os
import yaml

rootpath = ".."
datapath = os.path.join(rootpath, "data")

print("Scanning misuses...")

projects = {}

for filename in os.listdir(datapath):
    if filename.endswith(".yml"):
        filename = os.path.join(datapath, filename)
        file = open(filename, 'r')
        try:
            misuse = yaml.load(file)
            
            projectname = "<synthetic>"
            if "project" in misuse:
                projectname = misuse["project"]["name"]
            project = projects.get(projectname, {"misuses" : 0, "crashes" : 0})
            project["misuses"] += 1
            if misuse["crash"]:
                project["crashes"] += 1
            projects[projectname] = project
        except KeyError as e:
            print("Did not find '%s' in '%s'" % (e.args[0], filename))
        finally:
            file.close()

print
print("  %40s %10s %15s" % ("Project", "Misuses", "Crashes"))
for projectname in projects:
    project = projects[projectname]
    print("  %40s %10d %5d - % 6.1f%%" % (projectname, project["misuses"], project["crashes"], (project["crashes"] / project["misuses"] * 100)))
