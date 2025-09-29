from flask_wtf import FlaskForm
from wtforms import (
    IntegerField, SelectField, EmailField,
    PasswordField, SubmitField,
    StringField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length
import datetime


class LoginForm(FlaskForm):
    matric_number = IntegerField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    student_type = SelectField('Student Type', choices=[
        ('full-time', 'Full-Time'), 
        ('part-time', 'Part-Time')], 
        validators=[DataRequired()])
    submit = SubmitField("Login")


class CreateSuperAdminForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create Super Admin')

class AddStudentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    student_number = StringField('Student Number', validators=[DataRequired()])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[])
    submit = SubmitField('Add Student')

class AddLecturerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    staff_number = StringField('Staff Number', validators=[DataRequired()])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Lecturer')

class AddDepartmentForm2(FlaskForm):
    department_name = StringField('Department Name', validators=[DataRequired()])
    submit = SubmitField('Add Department')

class AssignLecturerForm(FlaskForm):
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    lecturer_id = SelectField('Lecturer', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Lecturer')

class AssignCourseForm(FlaskForm):
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    lecturer_id = SelectField('Lecturer', coerce=int, validators=[DataRequired()])
    course_name = StringField('Course Name', validators=[DataRequired()])
    submit = SubmitField('Assign Course')

class FacultyForm(FlaskForm):
    name = StringField(
        'Faculty Name', 
        validators=[DataRequired(), Length(max=100)]
    )
    submit = SubmitField('Create Faculty')

class AddDepartmentForm(FlaskForm):
    name = StringField(
        'Department Name', 
        validators=[DataRequired(), Length(max=100)]
    )
    faculty_id = SelectField(
        'Faculty', 
        coerce=int, 
        validators=[DataRequired()]
    )
    submit = SubmitField('Create Department')