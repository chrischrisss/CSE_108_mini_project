import { useState } from "react";
import Header from "../components/Header";

function AdminDashboard({
  user,
  adminData,
  adminLoading,
  adminMessage,
  adminAction,
  handleLogout,
}) {
  const [activeTab, setActiveTab] = useState("users");

  return (
    <div className="student-page">
      <div className="dashboard-card">
        <Header name={user.username} handleLogout={handleLogout} />

        <div className="dashboard-tabs">
          <button
            className={activeTab === "users" ? "tab-button active-tab" : "tab-button"}
            onClick={function () { setActiveTab("users"); }}
          >
            Users
          </button>
          <button
            className={activeTab === "courses" ? "tab-button active-tab" : "tab-button"}
            onClick={function () { setActiveTab("courses"); }}
          >
            Courses
          </button>
          <button
            className={activeTab === "enrollments" ? "tab-button active-tab" : "tab-button"}
            onClick={function () { setActiveTab("enrollments"); }}
          >
            Enrollments
          </button>
        </div>

        <main className="dashboard-content">
          {adminMessage !== "" && <p className="course-message">{adminMessage}</p>}
          {adminLoading && <p className="status-text">Loading admin data...</p>}

          {!adminLoading && activeTab === "users" && (
            <UsersPanel users={adminData.users} adminAction={adminAction} />
          )}
          {!adminLoading && activeTab === "courses" && (
            <CoursesPanel
              courses={adminData.courses}
              users={adminData.users}
              adminAction={adminAction}
            />
          )}
          {!adminLoading && activeTab === "enrollments" && (
            <EnrollmentsPanel
              enrollments={adminData.enrollments}
              users={adminData.users}
              courses={adminData.courses}
              adminAction={adminAction}
            />
          )}
        </main>
      </div>
    </div>
  );
}

function UsersPanel({ users, adminAction }) {
  const [newUser, setNewUser] = useState({ username: "", password: "", role: "student" });

  return (
    <>
      <h2>Create User</h2>
      <div className="admin-form">
        <input placeholder="Username" value={newUser.username} onChange={function (event) { setNewUser({ ...newUser, username: event.target.value }); }} />
        <input placeholder="Password" value={newUser.password} onChange={function (event) { setNewUser({ ...newUser, password: event.target.value }); }} />
        <select value={newUser.role} onChange={function (event) { setNewUser({ ...newUser, role: event.target.value }); }}>
          <option value="student">Student</option>
          <option value="teacher">Teacher</option>
          <option value="admin">Admin</option>
        </select>
        <button className="add-button" onClick={function () { adminAction("/admin/users", "POST", newUser); }}>Create</button>
      </div>

      <h2>Users</h2>
      <div className="table-container">
        <table className="course-table">
          <thead><tr><th>Username</th><th>Password</th><th>Role</th><th>Actions</th></tr></thead>
          <tbody>
            {users.map(function (user) {
              return <UserRow key={user.id} user={user} adminAction={adminAction} />;
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}

function UserRow({ user, adminAction }) {
  const [editedUser, setEditedUser] = useState({ username: user.username, password: "", role: user.role });

  return (
    <tr>
      <td><input value={editedUser.username} onChange={function (event) { setEditedUser({ ...editedUser, username: event.target.value }); }} /></td>
      <td><input type="password" placeholder="Enter password" value={editedUser.password} onChange={function (event) { setEditedUser({ ...editedUser, password: event.target.value }); }} /></td>
      <td><select value={editedUser.role} onChange={function (event) { setEditedUser({ ...editedUser, role: event.target.value }); }}><option value="student">Student</option><option value="teacher">Teacher</option><option value="admin">Admin</option></select></td>
      <td><button className="add-button" onClick={function () { adminAction(`/admin/users/${user.id}`, "PUT", editedUser); }}>Save</button> <button className="drop-button" onClick={function () { adminAction(`/admin/users/${user.id}`, "DELETE"); }}>Delete</button></td>
    </tr>
  );
}

function CoursesPanel({ courses, users, adminAction }) {
  const teachers = users.filter(function (user) { return user.role === "teacher"; });
  const [newCourse, setNewCourse] = useState({ name: "", capacity: "", teacher_id: "", time: "" });

  return (
    <>
      <h2>Create Course</h2>
      <div className="admin-form">
        <input placeholder="Course name" value={newCourse.name} onChange={function (event) { setNewCourse({ ...newCourse, name: event.target.value }); }} />
        <input type="number" min="1" placeholder="Capacity" value={newCourse.capacity} onChange={function (event) { setNewCourse({ ...newCourse, capacity: event.target.value }); }} />
        <select value={newCourse.teacher_id} onChange={function (event) { setNewCourse({ ...newCourse, teacher_id: event.target.value }); }}><option value="">Select teacher</option>{teachers.map(function (teacher) { return <option key={teacher.id} value={teacher.id}>{teacher.username}</option>; })}</select>
        <input placeholder="Class time" value={newCourse.time} onChange={function (event) { setNewCourse({ ...newCourse, time: event.target.value }); }} />
        <button className="add-button" onClick={function () { adminAction("/admin/courses", "POST", newCourse); }}>Create</button>
      </div>

      <h2>Courses</h2>
      <div className="table-container">
        <table className="course-table">
          <thead><tr><th>Name</th><th>Capacity</th><th>Teacher</th><th>Time</th><th>Actions</th></tr></thead>
          <tbody>{courses.map(function (course) { return <CourseRow key={course.id} course={course} teachers={teachers} adminAction={adminAction} />; })}</tbody>
        </table>
      </div>
    </>
  );
}

function CourseRow({ course, teachers, adminAction }) {
  const [editedCourse, setEditedCourse] = useState({ name: course.name, capacity: course.capacity, teacher_id: course.teacher_id, time: course.time });

  return (
    <tr>
      <td><input value={editedCourse.name} onChange={function (event) { setEditedCourse({ ...editedCourse, name: event.target.value }); }} /></td>
      <td><input type="number" min="1" value={editedCourse.capacity} onChange={function (event) { setEditedCourse({ ...editedCourse, capacity: event.target.value }); }} /></td>
      <td><select value={editedCourse.teacher_id} onChange={function (event) { setEditedCourse({ ...editedCourse, teacher_id: event.target.value }); }}>{teachers.map(function (teacher) { return <option key={teacher.id} value={teacher.id}>{teacher.username}</option>; })}</select></td>
      <td><input value={editedCourse.time} onChange={function (event) { setEditedCourse({ ...editedCourse, time: event.target.value }); }} /></td>
      <td><button className="add-button" onClick={function () { adminAction(`/admin/courses/${course.id}`, "PUT", editedCourse); }}>Save</button> <button className="drop-button" onClick={function () { adminAction(`/admin/courses/${course.id}`, "DELETE"); }}>Delete</button></td>
    </tr>
  );
}

function EnrollmentsPanel({ enrollments, users, courses, adminAction }) {
  const students = users.filter(function (user) { return user.role === "student"; });
  const [newEnrollment, setNewEnrollment] = useState({ student_id: "", course_id: "", grade: "" });

  return (
    <>
      <h2>Create Enrollment</h2>
      <div className="admin-form">
        <select value={newEnrollment.student_id} onChange={function (event) { setNewEnrollment({ ...newEnrollment, student_id: event.target.value }); }}><option value="">Select student</option>{students.map(function (student) { return <option key={student.id} value={student.id}>{student.username}</option>; })}</select>
        <select value={newEnrollment.course_id} onChange={function (event) { setNewEnrollment({ ...newEnrollment, course_id: event.target.value }); }}><option value="">Select course</option>{courses.map(function (course) { return <option key={course.id} value={course.id}>{course.name}</option>; })}</select>
        <input type="number" min="1" max="100" placeholder="Grade (1-100)" value={newEnrollment.grade} onChange={function (event) { setNewEnrollment({ ...newEnrollment, grade: event.target.value }); }} />
        <button className="add-button" onClick={function () { adminAction("/admin/enrollments", "POST", newEnrollment); }}>Create</button>
      </div>

      <h2>Enrollments</h2>
      <div className="table-container">
        <table className="course-table">
          <thead><tr><th>Student</th><th>Course</th><th>Grade</th><th>Actions</th></tr></thead>
          <tbody>{enrollments.map(function (enrollment) { return <EnrollmentRow key={enrollment.id} enrollment={enrollment} students={students} courses={courses} adminAction={adminAction} />; })}</tbody>
        </table>
      </div>
    </>
  );
}

function EnrollmentRow({ enrollment, students, courses, adminAction }) {
  const [editedEnrollment, setEditedEnrollment] = useState({ student_id: enrollment.student_id, course_id: enrollment.course_id, grade: enrollment.grade ?? "" });

  return (
    <tr>
      <td><select value={editedEnrollment.student_id} onChange={function (event) { setEditedEnrollment({ ...editedEnrollment, student_id: event.target.value }); }}>{students.map(function (student) { return <option key={student.id} value={student.id}>{student.username}</option>; })}</select></td>
      <td><select value={editedEnrollment.course_id} onChange={function (event) { setEditedEnrollment({ ...editedEnrollment, course_id: event.target.value }); }}>{courses.map(function (course) { return <option key={course.id} value={course.id}>{course.name}</option>; })}</select></td>
      <td><input type="number" min="1" max="100" value={editedEnrollment.grade} onChange={function (event) { setEditedEnrollment({ ...editedEnrollment, grade: event.target.value }); }} /></td>
      <td><button className="add-button" onClick={function () { adminAction(`/admin/enrollments/${enrollment.id}`, "PUT", editedEnrollment); }}>Save</button> <button className="drop-button" onClick={function () { adminAction(`/admin/enrollments/${enrollment.id}`, "DELETE"); }}>Delete</button></td>
    </tr>
  );
}

export default AdminDashboard;
