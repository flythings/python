import os
try:
	import requests
except ImportError:
	print ("Trying to Install required module: requests\n")
	os.system('python -m pip install requests')

try:
	import enum
except ImportError:
	print ("Trying to Install required module: enum\n")
	os.system('python -m pip install enum34')
# try:
# 	import pathlib
# except ImportError:
# 	print ("Trying to Install required module: pathlib\n")
# 	os.system('python -m pip install pathlib')

from flythings.client import search,sendObservation,sendObservations,login,setDevice,setSensor,setServer\
	,setToken,setTimeout,getObservation,setCustomHeader,setWorkspace,sendSocket,findSeries,sendRecord\
	,registerAction, registerActionForSeries,startActionListening, stopActionListening, ActionDataTypes\
	,loadDataByFile, setBatchEnabled, getObservationCSV, sendObservationsCSV, getHeaders
