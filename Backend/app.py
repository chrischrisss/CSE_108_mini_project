from models import *
from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt, \
    set_access_cookies, unset_jwt_cookies, verify_jwt_in_request

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink

app = Flask(__name__)

CORS(app, supports_credentials=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

app.config["SECRET_KEY"] = "super-secret-key"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False

db.init_app(app)

app.config["JWT_SECRET_KEY"] = "super-secret-key"

app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
jwt = JWTManager(app)

VALID_ROLES = ["student", "teacher", "admin"]

#created filler content for db to test (remember to change this to real names)
with app.app_context():

    db.create_all()

    if not User.query.filter_by(username="admin").first():
        admin_user = User(
            username="admin",
            password="password",
            role="admin"
        )

        db.session.add(admin_user)
        db.session.commit()

    student_names = [
        "Ava Johnson",
        "Liam Smith",
        "Emma Williams",
        "Noah Brown",
        "Olivia Davis",
        "Ethan Miller",
        "Sophia Wilson",
        "Mason Moore",
        "Isabella Taylor",
        "James Anderson"
    ]

    for student_name in student_names:
        if not User.query.filter_by(username=student_name).first():
            student = User(
                username=student_name,
                password="password",
                role="student"
            )
            db.session.add(student)

    db.session.commit()

    teacher_courses = [
        {
            "teacher": "Dr. Grace Lee",
            "course_one": "Introduction to Programming",
            "time_one": "MW 9:00-9:50 AM",
            "course_two": "Data Structures",
            "time_two": "MW 10:00-10:50 AM"
        },
        {
            "teacher": "Dr. Daniel Clark",
            "course_one": "Calculus I",
            "time_one": "TR 9:30-10:45 AM",
            "course_two": "Calculus II",
            "time_two": "TR 11:00 AM-12:15 PM"
        },
        {
            "teacher": "Dr. Mia Rodriguez",
            "course_one": "General Biology",
            "time_one": "MWF 11:00-11:50 AM",
            "course_two": "Genetics",
            "time_two": "MWF 1:00-1:50 PM"
        },
        {
            "teacher": "Dr. Henry Walker",
            "course_one": "World History",
            "time_one": "TR 1:00-2:15 PM",
            "course_two": "United States History",
            "time_two": "TR 2:30-3:45 PM"
        },
        {
            "teacher": "Dr. Chloe Harris",
            "course_one": "English Composition",
            "time_one": "MW 2:00-2:50 PM",
            "course_two": "Creative Writing",
            "time_two": "MW 3:00-3:50 PM"
        }
    ]

    for item in teacher_courses:
        teacher = User.query.filter_by(username=item["teacher"]).first()

        if not teacher:
            teacher = User(
                username=item["teacher"],
                password="password",
                role="teacher"
            )
            db.session.add(teacher)
            db.session.commit()

        if not Course.query.filter_by(name=item["course_one"]).first():
            course = Course(
                name=item["course_one"],
                capacity=30,
                time=item["time_one"],
                teacher_id=teacher.id
            )
            db.session.add(course)

        if not Course.query.filter_by(name=item["course_two"]).first():
            course = Course(
                name=item["course_two"],
                capacity=30,
                time=item["time_two"],
                teacher_id=teacher.id
            )
            db.session.add(course)

        db.session.commit()

admin = Admin(app, name="Course Registration Admin")


class AdminOnlyView(ModelView):
    def is_accessible(self):
        admin_id = session.get("admin")
        if admin_id:
            user = User.query.get(admin_id)
            if user and user.role == "admin":
                return True

        try:
            verify_jwt_in_request(optional=True)
            claims = get_jwt()
            return claims.get("role") == "admin"
        except Exception:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return "Forbidden", 403

    def on_model_change(self, form, model, is_created):
        if isinstance(model, User):
            if model.role not in VALID_ROLES:
                raise ValueError("Role must be student, teacher, or admin.")

            if model.role != "teacher":
                course = Course.query.filter_by(teacher_id=model.id).first()
                if course:
                    raise ValueError("A course teacher must have the teacher role.")

            if model.role != "student":
                enrollment = Enrollment.query.filter_by(student_id=model.id).first()
                if enrollment:
                    raise ValueError("An enrolled user must have the student role.")

        if isinstance(model, Course):
            if not isinstance(model.capacity, int) or model.capacity <= 0:
                raise ValueError("Course capacity must be a positive number.")

            teacher = User.query.get(model.teacher_id)
            if not teacher or teacher.role != "teacher":
                raise ValueError("The selected course teacher must have the teacher role.")

        if isinstance(model, Enrollment):
            student = User.query.get(model.student_id)
            if not student or student.role != "student":
                raise ValueError("The selected enrolled user must have the student role.")

            if model.grade is not None:
                if not isinstance(model.grade, int):
                    raise ValueError("Grade must be a number from 1 to 100.")

                if model.grade < 1 or model.grade > 100:
                    raise ValueError("Grade must be a number from 1 to 100.")


admin.add_view(AdminOnlyView(User, db.session))
admin.add_view(AdminOnlyView(Course, db.session))
admin.add_view(AdminOnlyView(Enrollment, db.session))
admin.add_link(MenuLink(name="Logout", url="/logout"))


@app.route("/admin-login", methods=["POST"])
def admin_login():
    data = request.get_json()

    user = User.query.filter_by(
        username=data["username"],
        password=data["password"]
    ).first()

    if not user or user.role != "admin":
        return {"error": "Forbidden"}, 403

    session["admin"] = user.id
    return {"message": "admin logged in"}



def require_role(role):
    claims = get_jwt()
    return claims.get("role") == role

@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "GET":
        return {"msg": "Login route exists"}

    data = request.get_json()
    username = data["username"]
    password = data["password"]

    user = User.query.filter_by(username=username, password=password).first()

    if not user:
        return jsonify({"msg": "Bad Credentials"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    if user.role == "admin":
        session["admin"] = user.id

    response = jsonify({"msg": "login successful"})
    set_access_cookies(response, access_token)

    return response


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("admin", None)
    
    if request.method == "GET":
        response = redirect("/")
    else:
        response = jsonify({"msg": "logged out"})

    unset_jwt_cookies(response)
    return response


@app.route("/dashboard")
@jwt_required()
def dashboard():
    return jsonify({"msg": "Authorized"})

#for student
@app.route("/courses")
@jwt_required()
def get_courses():


    claims = get_jwt()

    if claims["role"] != "student":
        return {"error": "Forbidden"}, 403

    courses = Course.query.all()

    result = []

    for course in courses:

        enrolled_count = Enrollment.query.filter_by(
            course_id=course.id
        ).count()

        result.append({
            "id": course.id,
            "name": course.name,
            "teacher": course.teacher.username,
            "capacity": course.capacity,
            "enrolled": enrolled_count,
            "time": course.time
        })

    return jsonify(result)

#for student
@app.route("/my-courses")
@jwt_required()
def my_courses():

    claims = get_jwt()

    if claims["role"] != "student":
        return {"error": "Forbidden"}, 403

    user_id = int(get_jwt_identity())

    enrollments = Enrollment.query.filter_by(
        student_id=user_id
    ).all()

    result = []

    for enrollment in enrollments:

        result.append({
            "course_id": enrollment.course.id,
            "course_name": enrollment.course.name,
            "grade": enrollment.grade,
            "time": enrollment.course.time
        })

    return jsonify(result)

#for student
@app.route("/enroll", methods=["POST"])
@jwt_required()
def enroll():

    claims = get_jwt()

    if claims["role"] != "student":
        return {"error": "Forbidden"}, 403

    student_id = int(get_jwt_identity())

    course_id = request.json["course_id"]

    course = Course.query.get(course_id)

    if not course:
        return {"error": "Course not found"}, 404

    current_count = Enrollment.query.filter_by(
        course_id=course_id
    ).count()

    if current_count >= course.capacity:
        return {"error": "Course full"}, 400

    existing = Enrollment.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()

    if existing:
        return {"error": "Already enrolled"}, 400

    enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id
    )

    db.session.add(enrollment)
    db.session.commit()

    return {"message": "Enrolled successfully"}

@app.route("/drop", methods=["POST"])
@jwt_required()
def drop_course():

    claims = get_jwt()

    if claims["role"] != "student":
        return {"error": "Forbidden"}, 403

    student_id = int(get_jwt_identity())
    course_id = request.json["course_id"]

    enrollment = Enrollment.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()

    if not enrollment:
        return {"error": "Not enrolled"}, 404

    db.session.delete(enrollment)
    db.session.commit()

    return {"message": "Dropped course"}




#for teacher

@app.route("/teacher/classes")
@jwt_required()
def teacher_classes():

    claims = get_jwt()

    if claims["role"] != "teacher":
        return {"error": "Forbidden"}, 403

    teacher_id = int(get_jwt_identity())

    courses = Course.query.filter_by(
        teacher_id=teacher_id
    ).all()

    result = []

    for course in courses:
        result.append({
            "id": course.id,
            "name": course.name,
            "capacity": course.capacity,
            "teacher": course.teacher.username,

            # ----------------- Add course time here ------------------
            "time": course.time
        })

    return jsonify(result)

#for teacher
@app.route("/teacher/class/<int:course_id>")
@jwt_required()
def teacher_roster(course_id):

    claims = get_jwt()

    if claims["role"] != "teacher":
        return {"error": "Forbidden"}, 403

    teacher_id = int(get_jwt_identity())

    course = Course.query.get(course_id)

    if not course:
        return {"error": "Course not found"}, 404

    if course.teacher_id != teacher_id:
        return {"error": "Forbidden"}, 403

    enrollments = Enrollment.query.filter_by(
        course_id=course_id
    ).all()

    result = []

    for enrollment in enrollments:

        result.append({
            "enrollment_id": enrollment.id,
            "student_id": enrollment.student.id,
            "username": enrollment.student.username,
            "grade": enrollment.grade
        })

    return jsonify(result)

#for teacher
@app.route("/teacher/grade", methods=["PUT"])
@jwt_required()
def update_grade():

    claims = get_jwt()

    if claims["role"] != "teacher":
        return {"error": "Forbidden"}, 403

    enrollment_id = request.json["enrollment_id"]
    grade = request.json["grade"]

    if grade == "" or grade is None:
        grade = None
    else:
        try:
            grade = int(grade)
        except (TypeError, ValueError):
            return {"error": "Grade must be a number from 1 to 100."}, 400

        if grade < 1 or grade > 100:
            return {"error": "Grade must be a number from 1 to 100."}, 400

    enrollment = Enrollment.query.get(enrollment_id)

    if not enrollment:
        return {"error": "Enrollment not found"}, 404

    teacher_id = int(get_jwt_identity())

    if enrollment.course.teacher_id != teacher_id:
        return {"error": "Forbidden"}, 403

    enrollment.grade = grade

    db.session.commit()

    return {"message": "Grade updated"}


# Admin API routes used by the React admin dashboard.
def admin_is_logged_in():
    claims = get_jwt()
    return claims["role"] == "admin"


def get_grade(grade):
    if grade == "" or grade is None:
        return None

    try:
        grade = int(grade)
    except (TypeError, ValueError):
        return "invalid"

    if grade < 1 or grade > 100:
        return "invalid"

    return grade


def user_can_have_role(user, role):
    if role not in VALID_ROLES:
        return False, "Role must be student, teacher, or admin."

    if role != "teacher":
        course = Course.query.filter_by(teacher_id=user.id).first()
        if course:
            return False, "A course teacher must have the teacher role."

    if role != "student":
        enrollment = Enrollment.query.filter_by(student_id=user.id).first()
        if enrollment:
            return False, "An enrolled user must have the student role."

    return True, ""


@app.route("/admin/data")
@jwt_required()
def admin_data():
    if not admin_is_logged_in():
        return {"error": "Forbidden"}, 403

    users = []
    for user in User.query.all():
        users.append({
            "id": user.id,
            "username": user.username,
            "role": user.role
        })

    courses = []
    for course in Course.query.all():
        courses.append({
            "id": course.id,
            "name": course.name,
            "capacity": course.capacity,
            "teacher_id": course.teacher_id,
            "teacher": course.teacher.username,
            "time": course.time or ""
        })

    enrollments = []
    for enrollment in Enrollment.query.all():
        enrollments.append({
            "id": enrollment.id,
            "student_id": enrollment.student_id,
            "student": enrollment.student.username,
            "course_id": enrollment.course_id,
            "course": enrollment.course.name,
            "grade": enrollment.grade
        })

    return jsonify({
        "users": users,
        "courses": courses,
        "enrollments": enrollments
    })


@app.route("/admin/users", methods=["POST"])
@jwt_required()
def create_user():
    if not admin_is_logged_in():
        return {"error": "Forbidden"}, 403

    data = request.json
    username = data["username"].strip()
    password = data["password"]
    role = data["role"]

    if username == "" or password == "":
        return {"error": "Username and password are required."}, 400

    if role not in VALID_ROLES:
        return {"error": "Role must be student, teacher, or admin."}, 400

    if User.query.filter_by(username=username).first():
        return {"error": "Username already exists."}, 400

    user = User(username=username, password=password, role=role)
    db.session.add(user)
    db.session.commit()

    return {"message": "User created."}


@app.route("/admin/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    if not admin_is_logged_in():
        return {"error": "Forbidden"}, 403

    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found."}, 404

    data = request.json
    username = data["username"].strip()
    password = data["password"]
    role = data["role"]

    if username == "":
        return {"error": "Username is required."}, 400

    other_user = User.query.filter_by(username=username).first()
    if other_user and other_user.id != user.id:
        return {"error": "Username already exists."}, 400

    can_change_role, message = user_can_have_role(user, role)
    if not can_change_role:
        return {"error": message}, 400

    user.username = username
    if password != "":
        user.password = password
    user.role = role
    db.session.commit()

    return {"message": "User updated."}


@app.route("/admin/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    if not admin_is_logged_in():
        return {"error": "Forbidden"}, 403

    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found."}, 404

    if Course.query.filter_by(teacher_id=user.id).first():
        return {"error": "Delete this user's courses first."}, 400

    if Enrollment.query.filter_by(student_id=user.id).first():
        return {"error": "Delete this user's enrollments first."}, 400

    db.session.delete(user)
    db.session.commit()

    return {"message": "User deleted."}


@app.route("/admin/courses", methods=["POST"])
@jwt_required()
def create_course():
    if not admin_is_logged_in():
        return {"error": "Forbidden"}, 403

    data = request.json
    name = data["name"].strip()
    time = data["time"].strip()

    try:
        capacity = int(data["capacity"])
        teacher_id = int(data["teacher_id"])
    except (TypeError, ValueError):
        return {"error": "Capacity and teacher must be valid numbers."}, 400

    if name == "" or capacity <= 0:
        return {"error": "Course name and a positive capacity are required."}, 400

    if Course.query.filter_by(name=name).first():
        return {"error": "Course name already exists."}, 400

    teacher = User.query.get(teacher_id)
    if not teacher or teacher.role != "teacher":
        return {"error": "The selected teacher must have the teacher role."}, 400

    course = Course(name=name, capacity=capacity, teacher_id=teacher_id, time=time)
    db.session.add(course)
    db.session.commit()

    return {"message": "Course created."}


@app.route("/admin/courses/<int:course_id>", methods=["PUT"])
@jwt_required()
def update_course(course_id):
    if not admin_is_logged_in():
        return {"error": "Forbidden"}, 403

    course = Course.query.get(course_id)
    if not course:
        return {"error": "Course not found."}, 404

    data = request.json
    name = data["name"].strip()
    time = data["time"].strip()

    try:
        capacity = int(data["capacity"])
        teacher_id = int(data["teacher_id"])
    except (TypeError, ValueError):
        return {"error": "Capacity and teacher must be valid numbers."}, 400

    if name == "" or capacity <= 0:
        return {"error": "Course name and a positive capacity are required."}, 400

    other_course = Course.query.filter_by(name=name).first()
    if other_course and other_course.id != course.id:
        return {"error": "Course name already exists."}, 400

    teacher = User.query.get(teacher_id)
    if not teacher or teacher.role != "teacher":
        return {"error": "The selected teacher must have the teacher role."}, 400

    current_count = Enrollment.query.filter_by(course_id=course.id).count()
    if capacity < current_count:
        return {"error": "Capacity cannot be below the current enrollment count."}, 400

    course.name = name
    course.capacity = capacity
    course.teacher_id = teacher_id
    course.time = time
    db.session.commit()

    return {"message": "Course updated."}


@app.route("/admin/courses/<int:course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    if not admin_is_logged_in():
        return {"error": "Forbidden"}, 403

    course = Course.query.get(course_id)
    if not course:
        return {"error": "Course not found."}, 404

    if Enrollment.query.filter_by(course_id=course.id).first():
        return {"error": "Delete this course's enrollments first."}, 400

    db.session.delete(course)
    db.session.commit()

    return {"message": "Course deleted."}


@app.route("/admin/enrollments", methods=["POST"])
@jwt_required()
def create_enrollment():
    if not admin_is_logged_in():
        return {"error": "Forbidden"}, 403

    data = request.json
    grade = get_grade(data["grade"])

    try:
        student_id = int(data["student_id"])
        course_id = int(data["course_id"])
    except (TypeError, ValueError):
        return {"error": "Student and course must be valid numbers."}, 400

    if grade == "invalid":
        return {"error": "Grade must be a number from 1 to 100."}, 400

    student = User.query.get(student_id)
    course = Course.query.get(course_id)
    if not student or student.role != "student":
        return {"error": "The selected user must have the student role."}, 400

    if not course:
        return {"error": "Course not found."}, 404

    current_count = Enrollment.query.filter_by(course_id=course_id).count()
    if current_count >= course.capacity:
        return {"error": "Course is full."}, 400

    if Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first():
        return {"error": "This student is already enrolled in the course."}, 400

    enrollment = Enrollment(student_id=student_id, course_id=course_id, grade=grade)
    db.session.add(enrollment)
    db.session.commit()

    return {"message": "Enrollment created."}


@app.route("/admin/enrollments/<int:enrollment_id>", methods=["PUT"])
@jwt_required()
def update_enrollment(enrollment_id):
    if not admin_is_logged_in():
        return {"error": "Forbidden"}, 403

    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return {"error": "Enrollment not found."}, 404

    data = request.json
    grade = get_grade(data["grade"])

    try:
        student_id = int(data["student_id"])
        course_id = int(data["course_id"])
    except (TypeError, ValueError):
        return {"error": "Student and course must be valid numbers."}, 400

    if grade == "invalid":
        return {"error": "Grade must be a number from 1 to 100."}, 400

    student = User.query.get(student_id)
    course = Course.query.get(course_id)
    if not student or student.role != "student":
        return {"error": "The selected user must have the student role."}, 400

    if not course:
        return {"error": "Course not found."}, 404

    current_count = Enrollment.query.filter_by(course_id=course_id).count()
    if course_id != enrollment.course_id:
        if current_count >= course.capacity:
            return {"error": "Course is full."}, 400

    other_enrollment = Enrollment.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()
    if other_enrollment and other_enrollment.id != enrollment.id:
        return {"error": "This student is already enrolled in the course."}, 400

    enrollment.student_id = student_id
    enrollment.course_id = course_id
    enrollment.grade = grade
    db.session.commit()

    return {"message": "Enrollment updated."}


@app.route("/admin/enrollments/<int:enrollment_id>", methods=["DELETE"])
@jwt_required()
def delete_enrollment(enrollment_id):
    if not admin_is_logged_in():
        return {"error": "Forbidden"}, 403

    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return {"error": "Enrollment not found."}, 404

    db.session.delete(enrollment)
    db.session.commit()

    return {"message": "Enrollment deleted."}


@app.route("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    })

if __name__ == "__main__":
    app.run(debug=True)
