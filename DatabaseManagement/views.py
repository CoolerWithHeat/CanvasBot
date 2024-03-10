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