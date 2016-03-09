import yaml
from os import listdir
from os.path import isfile, join

class YAMLReader:
        def readAllFrom(datapath, verbose):
            datafiles = [join(datapath, file) for file in listdir(datapath) if isfile(join(datapath, file)) and file.endswith(".yml")]

            data = []
            for file in datafiles:
                stream = open(file, 'r')
                try:
                    yamlContent = yaml.load(stream)
                    data.append(yamlContent)
                    if verbose:
                        print("Successfully added " + file)
                finally:
                    stream.close()
            return data

        def onAllDataDo(function, datapath, verbose):
            datafiles = [join(datapath, file) for file in listdir(datapath) if isfile(join(datapath, file)) and file.endswith(".yml")]

            result = []
            for file in datafiles:
                stream = open(file, 'r')
                try:
                    yamlContent = yaml.load(stream)
                    result.append(function(yamlContent))
                    if verbose:
                        print("Successfully added " + file)
                finally:
                    stream.close()
            return result
                    
class example:
    def f(data):
        print("f was called")

# example usage:
# datapath = r'<path>\MUBench\data'
# data = YAMLReader.readAllFrom(datapath, True)

# example usage:
datapath = r'<path>\MUBench\data'
results = YAMLReader.onAllDataDo(example.f, datapath, True)
print(results)
