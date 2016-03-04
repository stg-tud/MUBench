import yaml
from os import listdir
from os.path import isfile, join

class YAMLReader:
        def readAllFixingCommits(datapath, verbose):
            datafiles = [join(datapath, file) for file in listdir(datapath) if isfile(join(datapath, file)) and file.endswith(".yml")]

            data = []
            for file in datafiles:
                stream = open(file, 'r')
                try:
                    yamlContent = yaml.load(stream)
                    fixingCommit = yamlContent["fix"]["commit"]
                    data.append(fixingCommit)
                    if verbose:
                        print(fixingCommit)
                finally:
                    stream.close()
            return data

# example usage:
#datapath = '/home/pi/Documents/Eko/MUBench/data'
#fixingCommits = YAMLReader.readAllFixingCommits(datapath, True)


