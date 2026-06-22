from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __table_args__ = (
        db.CheckConstraint(
            "role IN ('student', 'teacher', 'admin')",
            name="valid_user_role"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False)


class Course(db.Model):
    __table_args__ = (
        db.CheckConstraint("capacity > 0", name="positive_course_capacity"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time = db.Column(db.String(50))

    teacher = db.relationship(
        "User",
        foreign_keys=[teacher_id]
    )


class Enrollment(db.Model):
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id'),
        db.CheckConstraint(
            "grade IS NULL OR (grade >= 1 AND grade <= 100)",
            name="valid_enrollment_grade"
        ),
    )
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    grade = db.Column(db.Integer)

    student = db.relationship(
        "User",
        foreign_keys=[student_id]
    )

    course = db.relationship(
        "Course",
        foreign_keys=[course_id]
    )
