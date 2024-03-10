from django.test import TestCase
import requests

base_url = 'http://localhost:8000/'

def create_student(student_data):
    endpoint = 'CreateStudent/'
    url = base_url + endpoint

    try:
        response = requests.post(url, json=student_data)
        if response.status_code == 201:
            print("Student created successfully!")
            print("Student details:", response.json())
        else:
            print("Failed to create student:", response.text)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

# student_data = {
#     "chat_id" : 54514842,
#     "student_name": "Mansur Davlatov",
# }
# create_student(student_data)

def update_student_data(student_id, data):
    endpoint = 'UpdateStudent/'
    url = base_url + endpoint + str(student_id)+'/'
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print("Student data updated successfully.")
        print(response.json())
    else:
        print("Failed to update student data.")
        print(response.text)

# data = {
#         "student_id": 5329978,
#         "student_token": "18~1BhjOVKVptNle0KvZA8hnMDV4hUK5T7ER82s9zvpua8rR8JteNQcvXZMbU7zcbnN",
#         "student_name": "Mansur",
#         "courses": [
#             {
#                 "course_id": 1451497,
#                 "course_name": "COSC 1570 5T SP 2024  Mathematics for Computer Science"
#             },
#             {
#                 "course_id": 1451238,
#                 "course_name": "COSC 2610 1T SP 2024  Operating Systems"
#             },
#             {
#                 "course_id": 1452126,
#                 "course_name": "COSC 2670 8T SP 2024  Network Principles"
#             },
#             {
#                 "course_id": 1451383,
#                 "course_name": "COSC 2710 1T SP 2024  Social Engineering and Society"
#             },
#             {
#                 "course_id": 1450481,
#                 "course_name": "KEYS 4008 1T SP 2024  Leading from Where You Are"
#             },
#             {
#                 "course_id": 1450541,
#                 "course_name": "MNGT 2500 2U SP 2024  Marketing"
#             }
#         ],
#     }

# update_student_data(54514842, data)
        
def GetStudent(chat_id):
    try:
        requested_id = 000000 if chat_id == "all" else chat_id
        endpoint = f'GetStudents/{requested_id}/'
        request = requests.get(base_url+endpoint)
        if request.status_code == 200:
            return request.json()
        
        return None
    except:
        return None

# result = GetStudent(54514842)