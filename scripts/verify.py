# 
# Checks PyYAML setup

try:
    print("Checking PyYAML...")
    import yaml
    print(" ok.")
	print("Checking request...")
	import urllib.request
	print(" ok.")
except ImportError:
    print(" failed! Please check your setup.")