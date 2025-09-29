from flask_wtf import FlaskForm
from wtforms import (
    SelectField, SelectMultipleField,
    PasswordField, SubmitField,
    StringField
)
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField
from models import Department, Level

class LoginForm(FlaskForm):
    matric_number = StringField('Matric Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    student_type = SelectField('Student Type', choices=[
        ('full-time', 'Full-Time'), 
        ('part-time', 'Part-Time')], 
        validators=[DataRequired()])
    submit = SubmitField("Login")


class AttendanceForm(FlaskForm):
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    student_ids = SelectMultipleField('Students', coerce=int, validators=[DataRequired()])
    status = SelectField('Status', choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Excused', 'Excused')], validators=[DataRequired()])
    submit = SubmitField('Mark Attendance')

def department_choices():
    return Department.query.all()

def level_choices():
    return Level.query.all()

class CreateClassForm(FlaskForm):
    course_code = StringField('Course Code', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    department = QuerySelectField(
        'Department', query_factory=department_choices,
        get_label='name', allow_blank=False,
        validators=[DataRequired()]
    )
    level = QuerySelectField(
        'Level', query_factory=level_choices,
        get_label='name', allow_blank=False,
        validators=[DataRequired()]
    )
    submit = SubmitField('Create Class')


class AttendanceForm(FlaskForm):
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    student_ids = SelectMultipleField('Students', coerce=int, validators=[DataRequired()])
    status = SelectField('Status', choices=[('present', 'Present'), ('absent', 'Absent')], validators=[DataRequired()])
    submit = SubmitField('Mark Attendance')  # ✅ REQUIRED