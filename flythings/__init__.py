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

from flythings.client import search, send_observation, send_observations, login, set_device, set_sensor, set_server \
    , set_token, set_authorization_token, set_timeout, get_observation, set_custom_header, set_workspace, send_socket, \
    find_series, send_record, register_action, register_action_for_series, start_action_listening, \
    stop_action_listening, ActionDataTypes, load_data_by_file, set_batch_enabled, get_observation_csv, \
    send_observations_csv, get_headers, api_get_request, send_alert, save_text_metadata, save_date_metadata, \
    send_progress_action, send_prediction, send_predictions, search_prediction
