import requests
import json
from pprint import pprint

def findActivities(courseName):
    response = requests.get('http://localhost:8080/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code=' + courseName[0:-1])
    CourseJSON = response.json()
    id = CourseJSON[0]['courseOffering']['id']
    registrationGroupResponse = requests.get("http://localhost:8080/waitlist/waitlistregistrationgroups?courseOfferingId=" + id).json()
    for entry in registrationGroupResponse:
        for section in entry['activityOfferings']:
            instructors = []
            for instructor in section['activityOffering']['instructors']:
                instructors.append(instructor['personName'])
            currentSeats = section['activitySeatCount']['used']
            maxSeats = section['activitySeatCount']['total']
            date = section['scheduleNames'][0]
            title = section['activityOffering']['formatOfferingName']
            print(f"INSTR: {';'.join(sorted(instructors))}, TITLE: {title},  {currentSeats}/{maxSeats}")
    

findActivities('CSCI1101 ')