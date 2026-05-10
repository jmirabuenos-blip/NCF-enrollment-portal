from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Student, Course, Department, Enrollment, UserProfile

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head', 'email']
    search_fields = ['name', 'code']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'credits', 'capacity']
    search_fields = ['name', 'code']
    list_filter = ['department', 'credits']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_number', 'name', 'email', 'department', 'gender']
    search_fields = ['name', 'student_number', 'email']
    list_filter = ['department', 'gender']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'grade', 'enrolled_date']
    search_fields = ['student__name', 'course__code']
    list_filter = ['status', 'enrolled_date']
    list_editable = ['status', 'grade']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    list_editable = ['role']