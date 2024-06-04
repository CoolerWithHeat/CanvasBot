import requests, pytz, time
from datetime import datetime
from pyrogram import Client as TelegramServer

bot_token = "7028351172:AAFLInmyCgvpMiFfcGrHzTf1dUzFFEGKtTM"
api_id = 28896453
api_hash = "64bb30aabff78bdac993050515e3ba6a"
timezone = pytz.timezone('Asia/Tashkent')
base_url = 'http://localhost:8000/'
app = TelegramServer(
    "WebsterBot",
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token
)

params = {
    'per_page': 50,
}

request_header = {}

def get_current_hour_in_tashkent():
    current_time_tashkent = datetime.now(timezone)
    return current_time_tashkent.hour

def get_current_minute_in_tashkent():
    current_time_tashkent = datetime.now(timezone)
    return current_time_tashkent.minute

def get_current_semester():
    current_date = datetime.now()
    if current_date.month >= 8 or current_date.month < 1 or (current_date.month == 1 and current_date.day < 5):
        return 'Fall', current_date.year
    elif current_date.month >= 1 and current_date.month < 5:
        return 'Spring', current_date.year
    else:
        return 'Summer', current_date.year
    
def get_semester(started_at):
    start_date = datetime.strptime(started_at, "%Y-%m-%dT%H:%M:%SZ")
    current_semester, current_year = get_current_semester()
    
    if start_date.year == current_year and get_current_semester()[0] == get_current_semester()[0]:
        return current_semester
    else:
        return None


def GetTextTime(hours):
    rounded_hour = round(hours, 3)
    minutes_fraction = rounded_hour - int(hours) 
    minutes = int(60 * minutes_fraction)
    hours = int(hours)
    return {'hours':hours, 'minutes':minutes}

def CheckDate(target_time, unlock_date_check=False):
    try:
        target_datetime = datetime.strptime(target_time, "%Y-%m-%dT%H:%M:%SZ")
        target_datetime = pytz.utc.localize(target_datetime).astimezone(timezone)
        current_datetime = datetime.now(timezone)
        
        if not unlock_date_check:
            if target_datetime <= current_datetime:
                return 0
            else:
                time_difference = (target_datetime - current_datetime).total_seconds() / 3600
                return time_difference
        else:
            if target_datetime >= current_datetime:
                return 0
            else:
                return 1
    except:
        return 0

def load_students():
    def GetStudent(chat_id):
        try:
            requested_id = 000000 if chat_id == "all" else chat_id
            endpoint = f'GetStudents/{requested_id}/'
            request = requests.get(base_url+endpoint)
            print(request, 'GetStudent Function')
            if request.status_code == 200:
                return request.json()
            
            return None
        except:
            return None
    return GetStudent('all') or []
    
def build_message(assignment_name, hours, minutes, course_name):
    student_message = f"<b>Assignment Closing In {'' if not hours else str(hours) + ' hours and '}{minutes} minutes !!!</b> \n\n {assignment_name}\n\n <i>{course_name}</i>\n"
    return student_message 

def CheckAssignmentsDates(course_id, chat_id, course_name='', request_header=None):
    if course_id and request_header:
        request = requests.get(f'https://worldclassroom.webster.edu/api/v1/courses/{course_id}/assignments', headers=request_header, params=params)
        if request.status_code == 200:
            parsedData = request.json()
            for eachData in parsedData:
                assignment_name = eachData.get('name')
                due_info = eachData.get('due_at')
                lockedInfo = eachData.get('lock_info')
                is_unlocked_assignment = lockedInfo.get('can_view') if lockedInfo else False
                hours_left = float(CheckDate(due_info))
                minutes_and_hours = GetTextTime(hours_left)
                hours = minutes_and_hours['hours']
                minutes = minutes_and_hours['minutes']
                needs_reminding = hours < 16
                if due_info and not is_unlocked_assignment and not (int(hours) == 0 and int(minutes) == 0) and needs_reminding:
                    message = build_message(assignment_name, hours, minutes, course_name)
                    SendMessage(chat_id, message)

def SendMessage(chat_id, text):
    
    if not app.is_connected: app.start()

    app.send_message(chat_id, text)

schedule = [9, 17, 22]

def GetClosestDate(current_value):
    if 8 <= current_value <= 16:
        return 17
    elif 18 <= current_value <= 21:
        return 22
    elif (22 <= current_value >= 7) or (current_value < 8):
        return 9
    else:
        return None
    
def GetNextSchedule(current_time_hour, target_time):
    if (current_time_hour > 12) and target_time > 12:
        return (abs(current_time_hour - target_time) * 60) - int(get_current_minute_in_tashkent())
    if current_time_hour > 12:
        hours = (current_time_hour - 24) - target_time
        return (abs(hours) * 60) - int(get_current_minute_in_tashkent())
    else:
        hours = current_time_hour - target_time
        return (abs(hours) * 60) - int(get_current_minute_in_tashkent())

while True:
    next_schedule = 0
    the_right_time = False
    students = load_students()
    current_time = get_current_hour_in_tashkent()
    next_time = GetClosestDate(int(current_time))
    next_schedule_minutes = GetNextSchedule(int(current_time), next_time)
    print("running at hour ", current_time)
    print("next schedule is after", next_schedule_minutes, "hours")
    next_schedule = next_schedule_minutes * 60
    try:
        print('Checking Student Schedules at time ', current_time)
        if students:
            schedule_overlap = 0
            for each_student in students:
                token = each_student.get('student_token')
                if token:
                    chat_id = each_student.get('chat_id')
                    name = each_student.get('student_name')
                    id = each_student.get('student_id')
                    student_courses = each_student.get('courses')
                    request_header = {'Authorization': f'Bearer {token}'}
                    for each_course in student_courses:
                        course_name = each_course.get('course_name')
                        course_id = each_course.get('course_id')
                        print(course_name)
                        CheckAssignmentsDates(course_id, chat_id, course_name, request_header)
        print(f'next schedule at {next_time}:00\nTashkentTime')
        time.sleep(next_schedule)
    except:
        print("cannot reach server!")
        pass