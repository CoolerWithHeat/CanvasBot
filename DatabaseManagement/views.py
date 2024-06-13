from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Student, Course
from .serializers import StudentSerializer, CourseSerializer

@api_view(['POST'])
def create_student(request):
    serializer = StudentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_student(request, chat_id):
    try:
        student = Student.objects.get(chat_id=chat_id)
    except Student.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    existing_data = StudentSerializer(student).data
    new_data = request.data
    courses_data = new_data.pop('courses', [])
    if courses_data:
        new_courses = []
        for course_data in courses_data:
            course_id = course_data.get('course_id')
            try:
                course = Course.objects.get(course_id=course_id)
            except Course.DoesNotExist:
                course_serializer = CourseSerializer(data=course_data)
                if course_serializer.is_valid():
                    course = course_serializer.save()
                else:
                    return Response(course_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            new_courses.append(course)
        student.courses.set(new_courses)
    updated_data = {**existing_data, **new_data}

    serializer = StudentSerializer(student, data=updated_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def create_course(request):
    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_course(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = CourseSerializer(course, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_courses(token):
    import requests
    request_header = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'include[]': 'assignments',
        'enrollment_state': 'active'
    }
    response = requests.get('https://worldclassroom.webster.edu/api/v1/courses', headers=request_header, params=params)
    
    if response.status_code == 200:
        parsed_data = response.json()
        all_courses = []
        for each in parsed_data:
            course_name = each.get('name')
            course_id = each.get('id')
            all_courses.append({'course_id': course_id, 'course_name': course_name})
        return all_courses
    return []

@api_view(['GET'])
def get_students(request, chat_id=None):
    if chat_id:
        try:
            student = Student.objects.get(chat_id=chat_id)
            serializer = StudentSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

@api_view(['POST'])
def ReloadStudent(request, chat_id=None):
    try:
        student = Student.objects.get(chat_id=chat_id)
        newly_added_courses = get_courses(student.student_token)
        student.courses.clear()
        for each_course in newly_added_courses:
            course_id = each_course.get('course_id')
            course_name = each_course.get('course_name')
            if course_id and course_name:
                course, created = Course.objects.get_or_create(course_id=course_id, course_name=course_name)
                student.courses.add(course)
        return Response(newly_added_courses, status=200)
    except Student.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def DeleteStudent(request, chat_id=None):
    try:
        student = Student.objects.get(chat_id=chat_id)
        deleted_student = StudentSerializer(student)
        student_data = deleted_student.data
        student.delete()
        return Response(student_data, status=200)
    except Student.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)