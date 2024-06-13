import requests, json, pytz
from datetime import datetime
from pyrogram import Client as TelegramServer

timezone = pytz.timezone('Asia/Tashkent')
bot_token = "7028351172:AAFLInmyCgvpMiFfcGrHzTf1dUzFFEGKtTM"
api_id = 28896453
api_hash = "64bb30aabff78bdac993050515e3ba6a"
base_url = 'http://localhost:8001/'
app = TelegramServer(
    "WebsterBot",
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token
)

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

def GetStudent(chat_id):
    try:
        requested_id = 000000 if chat_id == "all" else chat_id
        endpoint = f'GetStudents/{requested_id}/'
        request = requests.get(base_url+endpoint)
        print('Student Information Requested --> ', request.status_code,)
        if request.status_code == 200:
            return request.json()
        
        return None
    except:
        return None


def validate_canvas_token(api_token):
    validation_endpoint = "https://worldclassroom.webster.edu/api/v1/courses"
    headers = {"Authorization": f"Bearer {api_token}"}
    try:
        response = requests.get(validation_endpoint, headers=headers)
        if response.status_code == 200:
            return api_token
        else:
            return False
    except:
        return False

def update_user_data(id_value, field_to_update, new_value):
    def update_student_data(student_id, data):
        endpoint = 'UpdateStudent/'
        url = base_url + endpoint + str(student_id)+'/'
        headers = {'Content-Type': 'application/json'}
        response = requests.put(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    return update_student_data(id_value, {field_to_update: new_value})

def store_user_data(message_id, student_token, student_name):
    data = {
        'chat_id': message_id,
        'student_id': None,
        'student_token': student_token or None,
        'student_name': student_name or None,
        'courses': [],
        'previously_interacted': True,
    }
    new_student = create_student(data)

def retrieve_user_data(message_id):
    return GetStudent(message_id)

def load_courses(CHAT_ID):
    try:
        student_request = GetStudent(CHAT_ID)
        if student_request:
            return student_request.get('courses') or []
        return []
    except:
        return []

def search_course_by_id(course_list, course_id):
    for course in course_list:
        if course['course_id'] == course_id:
            return course
    return None

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

CanvasToken = ''
CoursesEndpoint = f'https://worldclassroom.webster.edu/api/v1/courses/'  
AssignmentsEndpoint = f"https://worldclassroom.webster.edu/api/v1/users/courses/1451238/assignments"
# QuizzEndpoints = f"https://worldclassroom.webster.edu/api/v1/courses/1451497/quizzes"
params = {
    'per_page': 50,
}

request_header = {
    'Authorization':f'Bearer {CanvasToken}'
}

def GetCourses(token):
    request_header = {
        'Authorization':f'Bearer {token}'
    }
    request = requests.get('https://worldclassroom.webster.edu/api/v1/courses?include[]=assignments&enrollment_state=active', headers=request_header, params=params)
    if request.status_code == 200:
        parsedData = request.json()
        all_courses = []
        for each in parsedData:
            course_name = each.get('name')
            course_id = each.get('id')
            all_courses.append({'course_id': course_id, 'course_name': course_name})
        return all_courses
    return []

def fetchCourses(token_provisioned):
    courses = GetCourses(token_provisioned)
    if len(courses) > 0:
        return courses
    
def build_task_message(assignment_name, hours, minutes, course_name):
    student_message = f"<b>Assignment Closing In {'' if not hours else str(hours) + ' hours and '}{minutes} minutes !!!</b> \n\n {assignment_name}\n\n <i>{course_name}</i>\n"
    return student_message 

def build_courses_message(student_name, courses):
    try:
        header = f"<b>Your Enrollments Are These Current Semester !!!</b>\n\n"
        merged_courses = ''
        for each_course in list(courses):
            course = f"*{each_course.get('course_name')}*\n"
            merged_courses += course
        return header + merged_courses
    except:
        return "Could Not Find You Schedule, Sorry"
    
async def CheckAssignmentsDates(message_id=000000, student_enrollments=None, student_identity=None, force_check=False):
    courses = student_enrollments
    reminded = 0
    if courses:
        for each in courses:
            course_id = each.get('course_id')
            if courses:
                "https://worldclassroom.webster.edu/api/v1/courses/"
                request = requests.get(f'https://worldclassroom.webster.edu/api/v1/courses/{course_id}/assignments', headers=student_identity, params=params)
                print(request.status_code)
                if request.status_code == 200:
                    parsedData = request.json()
                    for eachData in parsedData:
                        assignment_name = eachData.get('name')
                        course_name = search_course_by_id(courses, course_id).get('course_name')
                        due_info = eachData.get('due_at')
                        lockedInfo = eachData.get('lock_info')
                        is_unlocked_assignment = lockedInfo.get('can_view') if lockedInfo else False
                        hours_left = float(CheckDate(due_info))
                        minutes_and_hours = GetTextTime(hours_left)
                        hours = minutes_and_hours['hours']
                        minutes = minutes_and_hours['minutes']
                        needs_reminding = hours < 14 if not force_check else hours < 24
                        if due_info and not is_unlocked_assignment and not (int(hours) == 0 and int(minutes) == 0) and needs_reminding:
                            message = build_task_message(assignment_name, hours, minutes, course_name)
                            await SendMessage(message, message_id)
                            reminded += 1
                            break
    return reminded

def isCommand(sent_message):
    return sent_message[0] == '!'

async def reload_student_courses(student_id, callback):
    try:
        endpoint = f'ReloadStudent/{student_id}/'
        request = requests.post(base_url+endpoint)
        print('Student Information Reload Requested --> ', request.status_code)
        if request.status_code == 200:
            await callback()
            response = request.json()
            if isinstance(response, list):
                courses = '  '.join(str(f"    \n*{data.get('course_name')}*") for data in response)
                header = f"<b>\nHere is Your Updated Schedule :)</b>\n"
                final_message = f"{header}{courses}"
                if courses: await SendMessage(final_message, student_id)
            return None
    except:
        return None

async def unsubscribe_student(student_id, callback):
    try:
        endpoint = f'DeleteStudent/{student_id}/'
        request = requests.post(base_url+endpoint)
        print('Unsubscription Requested --> ', request.status_code)
        if request.status_code == 200: 
            response = request.json()
            await callback()
            await SendMessage('You Have Been Successfully Unsubscribed From This Program !', student_id)
    except:
        return None

async def show_commands(student_id, callback):
    try:
        available_commands = ['check >> checks for assignments deadline', '!reload >> reloads your schedule for up-to-date enrollments', '!unsubscribe >> deletes you from the bot completely']
        commands = ''.join(str(f"\n{command}") for command in available_commands)
        final_message = f"Here Are Commands To Interact With Me :)\n{commands}"
        await callback()
        await SendMessage(final_message, student_id)
    except:
        return None
    
async def SayCommandsNotFound(chat_id, student_name):
    await app.send_message(chat_id, f"Hi{student_name}! if you want me to check your assignments just message me CHECK\n\nor if you want to know all commands to interact just message me the word Commands")

@app.on_message()
async def HandleResponse(client, message):
    chat_id = message.chat.id
    message_id = message.id 
    loading_alert = await SendMessage("Give me a second please...", chat_id)
    sender = message.from_user.username
    bot_sent = str(sender) == "Webster_Canvas_Alerts_bot"
    if not bot_sent:
        student_identity= retrieve_user_data(chat_id)
        student_details = student_identity.get('student_token') if student_identity else None
        previous_interaction = student_identity.get('previously_interacted') if student_identity else False
        student_name = f" {student_identity.get('student_name') or ''}" if isinstance(student_identity, dict) else None or ''
        if student_details:
            try:
                incoming_message = message.text.lower()
                async def remove_loading_alert(): await app.delete_messages(chat_id, loading_alert)
                if isCommand(incoming_message):
                    if incoming_message == '!reload': return await reload_student_courses(chat_id, remove_loading_alert)
                    if incoming_message == '!unsubscribe': return await unsubscribe_student(chat_id, remove_loading_alert)
                    if incoming_message == '!commands': return  await show_commands(chat_id, remove_loading_alert)
                    else: await SayCommandsNotFound(chat_id, student_name)
                    return True
                else:
                    if incoming_message == 'commands': 
                        return await show_commands(chat_id, remove_loading_alert)
                    else:
                        if incoming_message == 'check':
                            request_header = {'Authorization': f'Bearer {student_details}'}
                            reminded = await CheckAssignmentsDates(chat_id, student_identity.get('courses') or [], request_header, True)
                            await remove_loading_alert()
                            await app.send_message(chat_id, "There You Go!" if reminded else "No Assignment Closing in 24 Hours :)")
                            return True
                        else:
                            await SayCommandsNotFound(chat_id, student_name)
            except:
                await app.send_message(chat_id, f"Hi{student_name}! I cannot interpret and understand media such as images or any other files, only the command CHECK.\n\nIf you want me to check your assignments just message me the word Check\n\nor if you want to know all commands to interact just message me the word Commands")
        else:
            if previous_interaction:
                saved = False
                token_provisioned = validate_canvas_token(message.text)
                if token_provisioned:
                    await app.delete_messages(chat_id, message_id)
                    saved = update_user_data(chat_id, 'student_token', message.text)
                    if saved:
                        all_courses = fetchCourses(token_provisioned)
                        student_details = GetStudentName(token_provisioned)
                        student_id = dict(student_details).get('student_id')
                        student_name = dict(student_details).get('student_name')
                        update_user_data(chat_id, 'courses', all_courses)
                        if student_name and student_id:
                            update_user_data(chat_id, 'student_id', student_id)
                            update_user_data(chat_id, 'student_name',  student_name)
                            courses_list = build_courses_message(student_name, all_courses)
                            await app.send_message(chat_id, f"Good {student_name}! Now I will be letting you know hours before your assignments close so you do not miss them")
                            await app.send_message(chat_id, str(courses_list))
                            await app.send_message(chat_id, str('You will receive notifications here 3 times on the day your assignments set to close'))
                elif not saved:
                    await app.send_message(chat_id, "It does not look like a valid token, please provide me a valid token of your Canvas account")
                    await app.delete_messages(chat_id, loading_alert)
            else:
                store_user_data(chat_id, None, None)
                await app.send_message(chat_id, "Welcome !\nI am Canvas Asistant, I will be keeping an eye on your Canvas account and let you know hours before course assignments close, please provide me your canvas token so that i will remind you of your assignments in case you forget them.")
        await app.delete_messages(chat_id, loading_alert)

async def SendMessage(text, chat_id):
    message = await app.send_message(chat_id, text)
    return message.id

def GetStudentName(student_token):
    request_header = {
        'Authorization':f'Bearer {student_token}'
    }
    request = requests.get('https://worldclassroom.webster.edu/api/v1/users/self', params=params, headers=request_header)
    if request.status_code == 200:
        canvasResponse = request.json()
        student_id = canvasResponse.get('id')
        name = canvasResponse.get('first_name') or canvasResponse.get('last_name')
        return {'student_name':name, 'student_id':student_id}
    else:
        return {}
    
app.run()