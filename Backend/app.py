from models import *
from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt, \
    set_access_cookies, unset_jwt_cookies, verify_jwt_in_request

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from sqlalchemy import inspect, text

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

#created filler content for db to test (remember to change this to real names)
with app.app_context():

    db.create_all()

    course_columns = inspect(db.engine).get_columns("course")
    course_column_names = [column["name"] for column in course_columns]

    if "time" not in course_column_names:
        db.session.execute(text("ALTER TABLE course ADD COLUMN time VARCHAR(50)"))
        db.session.commit()

    if not User.query.filter_by(username="admin").first():
        admin_user = User(
            username="admin",
            password="password",
            role="admin"
        )

        db.session.add(admin_user)
        db.session.commit()

    if not User.query.filter_by(username="student1").first():
        student = User(
            username="student1",
            password="password",
            role="student"
        )

        db.session.add(student)
        db.session.commit()


    teacher = User.query.filter_by(
        username="teacher1"
    ).first()

    if not teacher:

        teacher = User(
            username="teacher1",
            password="password",
            role="teacher"
        )

        db.session.add(teacher)
        db.session.commit()

    if not Course.query.filter_by(
        name="Math 101"
    ).first():

        course = Course(
            name="Math 101",
            capacity=30,
            time="TR 11:00-11:50 AM",
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

    enrollment = Enrollment.query.get(enrollment_id)

    if not enrollment:
        return {"error": "Enrollment not found"}, 404

    teacher_id = int(get_jwt_identity())

    if enrollment.course.teacher_id != teacher_id:
        return {"error": "Forbidden"}, 403

    enrollment.grade = grade

    db.session.commit()

    return {"message": "Grade updated"}

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/student")
@jwt_required()
def student_page():

    if not require_role("student"):
        return {"error": "Forbidden"}, 403

    return render_template("student.html")

@app.route("/teacher")
@jwt_required()
def teacher_page():

    if not require_role("teacher"):
        return {"error": "Forbidden"}, 403

    return render_template("teacher.html")

# @app.route("/admin")
# def admin_page():
#     return render_template("admin.html")

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
