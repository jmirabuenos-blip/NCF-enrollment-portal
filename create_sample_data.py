import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_final.settings')
django.setup()

from django.contrib.auth.models import User
from pos_app.models import UserProfile, Department, Course, Student, Enrollment
from datetime import date

print("Creating sample data...")

admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@ncf.edu'})
admin_user.set_password('admin123')
admin_user.save()
UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})

staff_user, _ = User.objects.get_or_create(username='staff', defaults={'email': 'staff@ncf.edu'})
staff_user.set_password('staff123')
staff_user.save()
UserProfile.objects.get_or_create(user=staff_user, defaults={'role': 'staff'})

user_user, _ = User.objects.get_or_create(username='user', defaults={'email': 'user@ncf.edu'})
user_user.set_password('user123')
user_user.save()
UserProfile.objects.get_or_create(user=user_user, defaults={'role': 'user'})

print("Users created: admin, staff, user")

ccs, _ = Department.objects.get_or_create(
    code='CCS',
    defaults={
        'name': 'College of Computer Studies',
        'head': 'Dr. Maria Santos',
        'email': 'ccs@ncf.edu'
    }
)

coe, _ = Department.objects.get_or_create(
    code='COE',
    defaults={
        'name': 'College of Engineering',
        'head': 'Dr. Juan Dela Cruz',
        'email': 'coe@ncf.edu'
    }
)

print("Departments created: CCS, COE")

cs101, _ = Course.objects.get_or_create(
    code='CS101',
    defaults={
        'name': 'Introduction to Programming',
        'department': ccs,
        'credits': 3,
        'capacity': 30,
        'description': 'Basic programming concepts using Python'
    }
)

cs102, _ = Course.objects.get_or_create(
    code='CS102',
    defaults={
        'name': 'Data Structures',
        'department': ccs,
        'credits': 3,
        'capacity': 30,
        'description': 'Fundamental data structures and algorithms'
    }
)

eng101, _ = Course.objects.get_or_create(
    code='ENG101',
    defaults={
        'name': 'Engineering Mathematics',
        'department': coe,
        'credits': 3,
        'capacity': 35,
        'description': 'Advanced mathematics for engineering students'
    }
)

print("Courses created: CS101, CS102, ENG101")

juan, _ = Student.objects.get_or_create(
    student_number='24-04804',
    defaults={
        'name': 'Juan POR YOU',
        'email': 'juan@student.ncf.edu',
        'phone': '09171234567',
        'department': ccs,
        'gender': 'M',
        'date_of_birth': date(2005, 3, 15),
        'address': 'Naga City, Camarines Sur'
    }
)

maria, _ = Student.objects.get_or_create(
    student_number='24-05123',
    defaults={
        'name': 'Maria MARIE MARIEA',
        'email': 'maria@student.ncf.edu',
        'phone': '09187654321',
        'department': ccs,
        'gender': 'F',
        'date_of_birth': date(2005, 7, 22),
        'address': 'Naga City, Camarines Sur'
    }
)

print("Students created: Juan Dela Cruz, Maria Santos")

Enrollment.objects.get_or_create(
    student=juan,
    course=cs101,
    defaults={'status': 'enrolled'}
)

Enrollment.objects.get_or_create(
    student=maria,
    course=cs102,
    defaults={'status': 'enrolled'}
)

print("Enrollments created")
print("\nSample data created successfully!")
print("\nLogin credentials:")
print("Admin: admin / admin123")
print("Staff: staff / staff123")
print("User: user / user123")
