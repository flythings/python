import os
try:
	import requests
except ImportError:
	print ("Trying to Install required module: requests\n")
	os.system('python -m pip install requests')
import flythingsClient