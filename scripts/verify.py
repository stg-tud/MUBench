# 
# Checks PyYAML setup

try:
    print "Checking PyYAML...",
    import yaml
    print " ok."
except ImportError:
    print " failed! Please check your setup."