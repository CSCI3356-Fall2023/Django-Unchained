import requests
import json
from pprint import pprint

response = requests.get('http://localhost:8080/waitlist/waitlistactivityofferings?personId=90000001&termId=kuali.atp.FA2023-2024')
for entry in response.json():
    pprint(entry['activityOffering'].keys())