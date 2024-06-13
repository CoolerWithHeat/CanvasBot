from django.db import models

class Course(models.Model):
    course_id = models.IntegerField()
    course_name = models.CharField(max_length=255)
    def __str__(self):
        return self.course_name

class Student(models.Model):
    chat_id = models.IntegerField(blank=False, null=False)
    student_id = models.IntegerField(blank=True, null=True)
    student_token = models.CharField(max_length=255, blank=True, null=True)
    student_name = models.CharField(max_length=255, blank=True, null=True)
    courses = models.ManyToManyField(Course)
    previously_interacted = models.BooleanField(default=True)
    def __str__(self):
        return self.student_name or "Webster Student"