import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup

def findActivities(courseName):
    response = requests.get('http://localhost:8080/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code=CSCI')
    data_list = []
    if response.status_code == 200:
        for entry in response.json():
            offering = entry['courseOffering']
            term = entry['term']
            requisite_ids = entry.get('courseOffering', {}).get('requisiteIds', [])
            req = []
            for id in requisite_ids:
                if id == offering['id']:
                    req.append(offering['name'])
            #'requisiteIds' is not the same as 'id' of requisites. Still exploring...#
            description_html = offering['descr']['plain']
            date_text = term['descr']['plain']
            soup = BeautifulSoup(description_html, 'html.parser')
            description_text = soup.get_text(separator=' ')
            new_response = requests.get('http://localhost:8080/waitlist/waitlistactivityofferings?courseOfferingId=' + offering['id'])
            course_info = {}

    

findActivities('CSCI4961 ')