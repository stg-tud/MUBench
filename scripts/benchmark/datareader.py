import yaml
from os import listdir
from os.path import isfile, join

def onAllDataDo(function, datapath, verbose):
    datafiles = [join(datapath, file) for file in listdir(datapath) if isfile(join(datapath, file)) and file.endswith(".yml")]

    result = []
    for i, file in enumerate(datafiles, start=1):
        stream = open(file, 'r')

        if verbose:
            print("({}/{}) files: now on {}".format(i, len(datafiles), file))
        
        try:
            yamlContent = yaml.load(stream)
            result.append(function(file, yamlContent))
        finally:
            stream.close()
            if verbose:
                print("------------------------------------------------------------")
            
    return result

# example usage:
#from pprint import pprint
#
#def f(file, data):
#    return "({} -> {})".format(file, data)
#
#datapath = r'<path>\MUBench\data'
#results = onAllDataDo(f, datapath, True)
#pprint(results)
