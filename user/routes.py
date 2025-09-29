from datetime import datetime
from functools import wraps
from flask import (
    Blueprint, render_template, redirect,
    url_for, request, flash, abort
)
from werkzeug.security import generate_password_hash
from models import (
    User, Student, Lecturer, Admin,
    Department, Course, db, Faculty, Semester,
    AttendanceRecord, ClassSession, Level
)
from .forms import (
    AttendanceForm, LoginForm, CreateClassForm
)
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash

user_bp = Blueprint('user', __name__, url_prefix='/')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    print(request.form)
    if login_form.validate_on_submit():
        student_number = login_form.matric_number.data  # Use student_number instead of matric_number
        password = login_form.password.data

        # Check Student (using student_number)
        user = Student.query.filter_by(student_number=student_number).first()

        # If not student, check Lecturer
        if not user:
            user = Lecturer.query.filter_by(staff_number=student_number).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("✅ Login successful", "success")
            if hasattr(user, 'role') and user.role == 'student':
                return redirect(url_for('user.dashboard'))
            elif hasattr(user, 'role') and user.role == 'lecturer':
                return redirect(url_for('user.dashboard'))
        else:
            flash("❌ Invalid login credentials", "danger")

    return render_template("common_view/login.html", login_form=login_form)

# ========== LOGOUT ==========
@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("✅ You've been logged out", "info")
    return redirect(url_for('login'))

@user_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'lecturer':
        return render_template("lecturer_view/lecturer_dashboard.html")
    elif current_user.role == 'student':
        user = current_user

        # Get classes for this student's dept & level
        classes = ClassSession.query.filter_by(
            department_id=user.department_id,
            level_id=user.level_id
        ).all()

        # Compute attendance stats
        total_classes = len(classes)
        attended = AttendanceRecord.query.filter_by(student_id=user.id, status='present').count()
        missed = AttendanceRecord.query.filter_by(student_id=user.id, status='absent').count()
        percentage = (attended / total_classes * 100) if total_classes > 0 else 0

        today = datetime.now().strftime("%A, %d %B %Y")
        return render_template('student_view/student_dashboard.html',
                           user=user,
                           stats={'attended': attended, 'missed': missed, 'percentage': int(percentage)},
                           classes=classes,
                           current_date=today)
    return redirect(url_for('user.login'))


@user_bp.route('/mark-attendance', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    if current_user.role != 'lecturer':
        flash("Access Denied", "danger")
        return redirect(url_for('user.login'))

    form = AttendanceForm()
    form.course_id.choices = [(c.id, c.name) for c in current_user.courses]

    # Always set all students as choices for validation
    all_students = Student.query.all()
    form.student_ids.choices = [(s.id, f"{s.name} ({s.student_number})") for s in all_students]

    selected_course_id = form.course_id.data or request.form.get('course_id', type=int)

    if form.validate_on_submit():
        selected_course = Course.query.get(form.course_id.data)
        students_selected = form.student_ids.data
        attendance_status = form.status.data

        for student_id in students_selected:
            new_record = AttendanceRecord(
                student_id=student_id,
                course_id=selected_course.id,
                lecturer_id=current_user.id,
                status=attendance_status
            )
            db.session.add(new_record)
        db.session.commit()

        flash(f"✅ Attendance successfully marked for {len(students_selected)} student(s).", "success")
        return redirect(url_for('user.mark_attendance'))

    return render_template(
        "lecturer_view/mark_attendance.html",
        form=form,
        selected_course_id=selected_course_id
    )


@user_bp.route('/student-list')
@login_required
def student_list():
    if current_user.role != 'lecturer':
        return redirect(url_for('user.login'))
    return render_template("lecturer_view/studentlist.html")


@user_bp.route('/notifications')
@login_required
def notifications():
    if current_user.role == 'lecturer':
        return render_template("lecturer_view/notifications.html")
    elif current_user.role == 'student':
        return render_template("student_view/notifications.html")
    return redirect(url_for('user.login'))


@user_bp.route('/settings')
@login_required
def settings():
    if current_user.role == 'lecturer':
        return render_template("lecturer_view/settings.html", user=current_user)
    elif current_user.role == 'student':
        return render_template("student_view/settings.html", user=current_user)
    return redirect(url_for('user.login'))


@user_bp.route('/attendance-record')
@login_required
def attendance_record():
    if current_user.role == 'student':
        semester_id = request.args.get('semester')
        course_id = request.args.get('course')
        date = request.args.get('date')

        query = AttendanceRecord.query.join(
            Course
        ).filter(
            AttendanceRecord.student_id == current_user.id
        )
        # AttendanceRecord.query.filter_by(student_id=current_user.id)
        
        if semester_id:
            query = query.join(AttendanceRecord.course).filter(Course.semester_id == semester_id)
        if course_id:
            query = query.filter_by(course_id=course_id)
        if date:
            query = query.filter(db.func.date(AttendanceRecord.timestamp) == date)
        
        records = query.order_by(AttendanceRecord.timestamp.desc()).all()

        present_count = sum(1 for r in records if r.status == 'Present')
        absent_count = sum(1 for r in records if r.status == 'Absent')

        semesters = Semester.query.all()
        courses = [
            {"id": course.id, "name": course.name}
            for course in current_user.courses
        ]
        # Course.query.filter_by(lecturer_id=current_user.lecturer_id).all()
        # records = AttendanceRecord.query.filter_by(student_id=current_user.id).order_by(AttendanceRecord.timestamp.desc()).all()
        return render_template(
            "student_view/view_attendance.html",
            records=records,
            present_count=present_count,
            absent_count=absent_count,
            semesters=semesters,
            courses=courses
        )

    elif current_user.role == 'lecturer':
        # Could show history of *their own* marked records
        records = AttendanceRecord.query.filter_by(lecturer_id=current_user.id).order_by(AttendanceRecord.timestamp.desc()).all()
        return render_template(
            "lecturer_view/manage_attendance.html",
            attendance_records=records,
            departments=Department.query.all(),
            levels=Level.query.all(),
            courses=Course.query.all()
        )
    
    return redirect(url_for('user.login'))

@user_bp.route('/create-class', methods=['GET', 'POST'])
@login_required
def create_class():
    form = CreateClassForm()
    if form.validate_on_submit():
        new_class = ClassSession(
            course_code=form.course_code.data,
            title=form.title.data,
            time=form.time.data,
            department=form.department.data,  # This is a Department instance
            level=form.level.data,
            lecturer_id=current_user.id
        )
        db.session.add(new_class)
        db.session.commit()
        flash('Class created successfully!', 'success')
        return redirect(url_for('user.dashboard'))
    return render_template('lecturer_view/create_class.html',
                           form=form)

@user_bp.route('/get-students/<int:course_id>')
@login_required
def get_students(course_id):
    students = Student.query.all()
    student_list = [
        {
            "id": s.id,  # Use 'id', not 'student_id'
            "name": s.name,
            "student_number": s.student_number
        }
        for s in students
    ]
    return {"students": student_list}
