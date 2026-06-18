from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    teacher = db.relationship(
        "User",
        foreign_keys=[teacher_id]
    )


class Enrollment(db.Model):
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id'),
    )
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    grade = db.Column(db.String(5))

    student = db.relationship(
        "User",
        foreign_keys=[student_id]
    )

    course = db.relationship(
        "Course",
        foreign_keys=[course_id]
    )
