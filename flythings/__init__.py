import os
try:
	import requests
except ImportError:
	print ("Trying to Install required module: requests\n")
	os.system('python -m pip install requests')

from flythings.client import search,sendObservation,sendObservations,login,setDevice,setSensor,setServer,setToken,setTimeout,getObservation,setCustomHeader,setWorkspace,sendSocket,findSeries