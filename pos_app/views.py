from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Count
from functools import wraps
from .models import Student, Course, Department, Enrollment, UserProfile
from .forms import StudentForm, CourseForm, DepartmentForm, EnrollmentForm

def get_role(user):
    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return 'user'

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if get_role(request.user) != 'admin':
            messages.error(request, 'Admin access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if get_role(request.user) not in ['admin', 'staff']:
            messages.error(request, 'Staff access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def home(request):
    return render(request, 'pos_app/home.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role='user')
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'pos_app/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'user'})
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'pos_app/login.html')

def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def dashboard(request):
    role = get_role(request.user)
    
    try:
        student = request.user.student_profile
        my_enrollments = Enrollment.objects.filter(student=student).order_by('-enrolled_date')[:5]
    except:
        student = None
        my_enrollments = []
    
    context = {
        'role': role,
        'student': student,
        'my_enrollments': my_enrollments,
        'total_students': Student.objects.count(),
        'total_courses': Course.objects.count(),
        'total_departments': Department.objects.count(),
        'total_enrollments': Enrollment.objects.filter(status='enrolled').count(),
        'departments': Department.objects.annotate(student_count=Count('student')),
        'recent_students': Student.objects.all().order_by('-created_at')[:5],
    }
    return render(request, 'pos_app/dashboard.html', context)

@login_required
def student_list(request):
    students = Student.objects.all().order_by('-created_at')
    return render(request, 'pos_app/students/list.html', {'students': students})

@login_required
def student_create(request):
    role = get_role(request.user)
    
    if role == 'user':
        try:
            student = request.user.student_profile
            messages.info(request, 'You already have a student profile. Edit it instead.')
            return redirect('student_edit', pk=student.pk)
        except:
            pass
    
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            if role == 'user':
                student.user = request.user
            student.save()
            messages.success(request, 'Student profile created successfully!')
            return redirect('student_list')
    else:
        if role == 'user':
            form = StudentForm(initial={'email': request.user.email})
        else:
            form = StudentForm()
    return render(request, 'pos_app/students/form.html', {'form': form, 'title': 'Add Student'})

@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    role = get_role(request.user)
    
    try:
        is_own = student.user == request.user
    except:
        is_own = False
    
    if role not in ['admin', 'staff'] and not is_own:
        messages.error(request, 'You can only edit your own profile!')
        return redirect('student_list')
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student profile updated successfully!')
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'pos_app/students/form.html', {'form': form, 'title': 'Edit Student'})

@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('student_list')
    return render(request, 'pos_app/students/confirm_delete.html', {'student': student})

@login_required
def course_list(request):
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'pos_app/courses/list.html', {'courses': courses})

@admin_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully!')
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'pos_app/courses/form.html', {'form': form, 'title': 'Add Course'})

@admin_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'pos_app/courses/form.html', {'form': form, 'title': 'Edit Course'})

@admin_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('course_list')
    return render(request, 'pos_app/courses/confirm_delete.html', {'course': course})

@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'pos_app/departments/list.html', {'departments': departments})

@admin_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department added successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'pos_app/departments/form.html', {'form': form, 'title': 'Add Department'})

@admin_required
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'pos_app/departments/form.html', {'form': form, 'title': 'Edit Department'})

@admin_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully!')
        return redirect('department_list')
    return render(request, 'pos_app/departments/confirm_delete.html', {'department': department})

@login_required
def enrollment_list(request):
    role = get_role(request.user)
    if role in ['admin', 'staff']:
        enrollments = Enrollment.objects.all().order_by('-enrolled_date')
    else:
        try:
            student = request.user.student_profile
            enrollments = Enrollment.objects.filter(student=student).order_by('-enrolled_date')
        except:
            enrollments = []
    return render(request, 'pos_app/enrollments/list.html', {'enrollments': enrollments})

@login_required
def enrollment_create(request):
    role = get_role(request.user)
    
    try:
        student = request.user.student_profile
    except:
        student = None
    
    if request.method == 'POST':
        if role in ['admin', 'staff']:
            form = EnrollmentForm(request.POST)
        else:
            if not student:
                messages.error(request, 'You need to create a student profile first!')
                return redirect('student_create')
            form = EnrollmentForm(request.POST)
            
        if form.is_valid():
            enrollment = form.save(commit=False)
            
            if role == 'user' and student:
                enrollment.student = student
                
            if enrollment.course.enrollment_set.filter(status__in=['pending', 'enrolled']).count() >= enrollment.course.capacity:
                messages.error(request, 'Course is at full capacity!')
            else:
                enrollment.save()
                messages.success(request, 'Enrollment created successfully!')
                return redirect('enrollment_list')
    else:
        if role == 'user' and student:
            form = EnrollmentForm(initial={'student': student})
        else:
            form = EnrollmentForm()
    return render(request, 'pos_app/enrollments/form.html', {'form': form, 'title': 'Create Enrollment'})

@login_required
def enrollment_cancel(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    
    role = get_role(request.user)
    try:
        student = request.user.student_profile
        is_own = enrollment.student == student
    except:
        is_own = False
    
    if role not in ['admin', 'staff'] and not is_own:
        messages.error(request, 'You can only cancel your own enrollments!')
        return redirect('enrollment_list')
    
    if enrollment.status == 'pending':
        if request.method == 'POST':
            enrollment.status = 'dropped'
            enrollment.save()
            messages.success(request, 'Enrollment cancelled successfully!')
            return redirect('enrollment_list')
        return render(request, 'pos_app/enrollments/confirm_cancel.html', {'enrollment': enrollment})
    else:
        messages.error(request, 'Only pending enrollments can be cancelled!')
        return redirect('enrollment_list')

@admin_required
def user_list(request):
    profiles = UserProfile.objects.select_related('user').all()
    return render(request, 'pos_app/users/list.html', {'profiles': profiles})

@admin_required
def user_change_role(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['admin', 'staff', 'user']:
            profile.role = new_role
            profile.save()
            messages.success(request, f'Role updated for {profile.user.username}.')
        return redirect('user_list')
    return render(request, 'pos_app/users/change_role.html', {'profile': profile})