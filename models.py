from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    relationship
)

from sqlalchemy import create_engine, Integer, Column, String
from flask_login import UserMixin
from config import config
from werkzeug.security import generate_password_hash



db_name = config.SQLALCHEMY_DATABASE_URI
print(db_name)
engine = create_engine(db_name, echo=True)

class ModelBase(DeclarativeBase):
    pass

# Create db instance (but don't initialize yet)
db = SQLAlchemy(model_class=ModelBase)

student_course_table = db.Table(
    'student_course',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)

lecturer_student_table = db.Table(
    'lecturer_student',
    db.Column('lecturer_id', db.Integer, db.ForeignKey('lecturer.id')),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'))
)


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    role: Mapped[str] = mapped_column(db.String(50), nullable=False)
    type: Mapped[str] = mapped_column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Student(User):
    __tablename__ = 'student'

    id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), primary_key=True)
    student_number: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    department_id: Mapped[int] = mapped_column(db.ForeignKey('department.id'))
    faculty_id: Mapped[int] = mapped_column(db.ForeignKey('faculty.id'))
    level_id: Mapped[int] = mapped_column(db.ForeignKey('level.id'))

    level = relationship('Level', back_populates='students')
    department = relationship('Department', back_populates='students')
    faculty = relationship('Faculty')
    courses = relationship('Course', secondary=student_course_table, back_populates='students')
    lecturers = relationship('Lecturer', secondary=lecturer_student_table, back_populates='students')

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

    def __repr__(self):
        return f"<Student {self.name} ({self.student_number})>"


class Lecturer(User):
    __tablename__ = 'lecturer'

    id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), primary_key=True)
    staff_number: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    department_id: Mapped[int] = mapped_column(db.ForeignKey('department.id'))
    faculty_id: Mapped[int] = mapped_column(db.ForeignKey('faculty.id'))

    department = relationship('Department', back_populates='lecturers')
    faculty = relationship('Faculty')
    courses = relationship('Course', back_populates='lecturer')
    students = relationship('Student', secondary=lecturer_student_table, back_populates='lecturers')

    __mapper_args__ = {
        'polymorphic_identity': 'lecturer',
    }

    def __repr__(self):
        return f"<Lecturer {self.name} ({self.staff_number})>"


class Admin(User):
    __tablename__ = 'admin'

    id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), primary_key=True)
    admin_level: Mapped[str] = mapped_column(db.String(50), default='standard')

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    def __repr__(self):
        return f"<Admin {self.name} (Level: {self.admin_level})>"


class Department(db.Model):
    __tablename__ = 'department'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    faculty_id: Mapped[int] = mapped_column(db.ForeignKey('faculty.id'))

    faculty = relationship('Faculty', back_populates='departments')
    lecturers = relationship('Lecturer', back_populates='department', cascade='all, delete-orphan')
    students = relationship('Student', back_populates='department', cascade='all, delete-orphan')
    courses = relationship('Course', back_populates='department', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Department {self.name} in Faculty {self.faculty_id}>"

class Semester(db.Model):
    __tablename__ = 'semester'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)

    courses = relationship('Course', back_populates='semester', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Semester {self.name}>"

class Level(db.Model):
    __tablename__ = 'level'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)
    students = relationship('Student', back_populates='level', cascade='all, delete-orphan')

    def __repr__(self):
        return f"{self.name}"

class Course(db.Model):
    __tablename__ = 'course'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    department_id: Mapped[int] = mapped_column(db.ForeignKey('department.id'))
    lecturer_id: Mapped[int] = mapped_column(db.ForeignKey('lecturer.id'), nullable=True)
    semester_id: Mapped[int] = mapped_column(db.ForeignKey('semester.id'), nullable=False)

    department = relationship("Department", back_populates="courses")
    lecturer = relationship("Lecturer", back_populates="courses")
    students = relationship("Student", secondary=student_course_table, back_populates="courses")
    semester = relationship('Semester', back_populates='courses')

    def __repr__(self):
        return f"<Course {self.name}>"


class Faculty(db.Model):
    __tablename__ = 'faculty'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)

    departments = relationship('Department', back_populates='faculty', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Faculty {self.name}>"


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_record'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(db.ForeignKey('student.id'), nullable=False)
    course_id: Mapped[int] = mapped_column(db.ForeignKey('course.id'), nullable=False)
    lecturer_id: Mapped[int] = mapped_column(db.ForeignKey('lecturer.id'), nullable=False)
    class_session_id: Mapped[int] = mapped_column(db.ForeignKey('class_session_record.id'), nullable=True)
    
    status: Mapped[str] = mapped_column(db.String(20), nullable=False, default="Present")
    timestamp: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)

    student = relationship('Student')
    course = relationship('Course')
    lecturer = relationship('Lecturer')
    class_session = relationship('ClassSession', backref='attendance_records')

    def __repr__(self):
        return f"<AttendanceRecord Student={self.student_id}, Course={self.course_id}, Status={self.status}>"

class ClassSession(db.Model):
    __tablename__ = 'class_session_record'

    id: Mapped[int] = mapped_column(primary_key=True)
    course_code: Mapped[str] = mapped_column(db.String(20), nullable=False)
    title: Mapped[str] = mapped_column(db.String(100), nullable=False)
    time: Mapped[str] = mapped_column(db.String(50), nullable=False)
    department_id: Mapped[int] = mapped_column(db.ForeignKey('department.id'), nullable=False)
    department: Mapped["Department"] = relationship('Department', backref=db.backref('classes', lazy=True))
    level_id: Mapped[int] = mapped_column(db.ForeignKey('level.id'), nullable=False)
    level: Mapped["Level"] = relationship('Level', backref=db.backref('levels', lazy=True))
    lecturer_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('lecturer.id'))
    lecturer: Mapped["Lecturer"] = relationship('Lecturer')
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)

    def attendance_for_student(self, student_id):
        return AttendanceRecord.query.filter_by(class_id=self.id, student_id=student_id).first()

# Function to create tables
def create_tables(app):
    with app.app_context():
        # declarative_base().metadata.create_all(engine)
        db.create_all()
        print("Tables created successfully.")

def create_super_admin(app):
    """Create a default super admin user."""
    with app.app_context():
        create_new_user  = input("Creating new super admin! Press Enter to continue or Q to skip... ")
        if create_new_user.lower() == "q":
            return
        email = input('Email: ')
        name = input('Name: ')
        password = input('Password: ')
        hashed_pw = generate_password_hash(password)

        admin = Admin(
            email=email,
            password=hashed_pw,
            name=name,
            role='admin',
            admin_level='super'
        )
        db.session.add(admin)
        db.session.commit()
        # if response:
        print(f"✅ Super admin '{email}' created!")

def create_semester(app):
    with app.app_context():
        create_semester = input("Press Enter to create the Semester or Q to skip: ")
        if create_semester.lower() == "q":
            return
        semesters = ['First Semester', 'Second Semester']
        for name in semesters:
            if not Semester.query.filter_by(name=name).first():
                db.session.add(Semester(name=name))
        db.session.commit()
        print("✅ Semesters seeded.")

def create_levels(app):
    with app.app_context():
        create_levels = input("Press Enter to create the Levels or Q to skip: ")
        if create_levels.lower() == "q":
            return
        levels = ['ND1', 'ND2', 'HND1', 'HND2']
        for name in levels:
            if not Level.query.filter_by(name=name).first():
                db.session.add(Level(name=name))
        db.session.commit()
        print("✅ Levels seeded.")
