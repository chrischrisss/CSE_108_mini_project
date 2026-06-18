from models import *
from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt, \
    set_access_cookies, unset_jwt_cookies

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
db.init_app(app)

#created filler content for db to test (remember to change this to real names)
with app.app_context():

    db.create_all()

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
            teacher_id=teacher.id
        )

        db.session.add(course)
        db.session.commit()



app.config["JWT_SECRET_KEY"] = "super-secret-key"

app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
jwt = JWTManager(app)


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

    response = jsonify({"msg": "login successful"})
    set_access_cookies(response, access_token)  # 👈 KEY CHANGE

    return response


@app.route("/logout", methods=["POST"])
def logout():
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
            "grade": enrollment.grade
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
            "teacher": course.teacher.username
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
    return {
        "user_id": get_jwt_identity(),
        "role": get_jwt()["role"]
    }

if __name__ == "__main__":
    app.run(debug=True)
