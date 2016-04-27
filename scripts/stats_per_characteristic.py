#
# Prints statistics about the API misuses per characteristic.
#
from __future__ import division
import os
import yaml

rootpath = ".."
datapath = os.path.join(rootpath, "data")

print("Scanning misuses...")

statistics = {}

for filename in os.listdir(datapath):
    if filename.endswith(".yml"):
        filename = os.path.join(datapath, filename)
        file = open(filename, 'r')
        try:
            misuse = yaml.load(file)

            chars = misuse["characteristics"]
            for char in chars:
                seg = char.split('/')
                stat = statistics.get(seg[0], {"total" : {"misuses" : 0, "crashes" : 0}})
                stat["total"]["misuses"] += 1
                if misuse["crash"]:
                    stat["total"]["crashes"] += 1
                
                if len(seg) > 1:
                    segstat = stat.get(seg[1], {"misuses" : 0, "crashes" : 0})
                    segstat["misuses"] += 1
                    if misuse["crash"]:
                        segstat["crashes"] += 1
                    stat[seg[1]] = segstat
                    
                statistics[seg[0]] = stat
        
        finally:
            file.close()

print
print("%25s %25s %7s %14s" % ("Characteristic", "SubCharacteristic", "Misuses", "Crashes"))
for statname in statistics:
    stat = statistics[statname]
    for segstat in stat:
        print("%25s %25s %7d %7d% 6.1f%%" % (statname, segstat, stat[segstat]["misuses"], stat[segstat]["crashes"], (stat[segstat]["crashes"] / stat[segstat]["misuses"] * 100)))

