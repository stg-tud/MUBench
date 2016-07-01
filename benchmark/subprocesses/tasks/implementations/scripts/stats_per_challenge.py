#
# Prints statistics about the API misuses per characteristic.
#
from __future__ import division
import os
import yaml

rootpath = ".."
datapath = os.path.join(rootpath, "data")

print("Scanning misuses in '%s'" % datapath)

statistics = {}

for filename in os.listdir(datapath):
    if filename.endswith(".yml"):
        filename = os.path.join(datapath, filename)
        file = open(filename, 'r')
        try:
            misuse = yaml.load(file)

            if "challenges" in misuse:
                challs = misuse["challenges"]
                for chall in challs:
                    stat = statistics.get(chall, 0)
                    stat += 1
                    statistics[chall] = stat
        
        finally:
            file.close()

print
print("%25s %7s" % ("Challenge", "Misuses"))
for statname in statistics:
    print("%25s %7d" % (statname, statistics[statname]))

