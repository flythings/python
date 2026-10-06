# flythings/__init__.py
import os

try:
    import requests
except ImportError:
    print("Trying to Install required module: requests\n")
    os.system('python -m pip install requests')

try:
    import enum
except ImportError:
    print("Trying to Install required module: enum\n")
    os.system('python -m pip install enum34')
# try:
# 	import pathlib
# except ImportError:
# 	print ("Trying to Install required module: pathlib\n")
# 	os.system('python -m pip install pathlib')

from flythings.config import ServerConfig

import flythings.paths

from flythings.base_client import BaseClient

from flythings.modules.action import ActionModule, ActionDataTypes
from flythings.modules.insertion import InsertionModule
from flythings.modules.prediction import PredictionModule
from flythings.modules.realtime import RealTimeModule
from flythings.modules.sos import SosModule, SamplingFeatureType
from flythings.modules.util import UtilModule
