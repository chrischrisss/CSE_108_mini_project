import { useState } from "react";
import Header from "../components/Header";

function StudentDashboard({
  user,
  myCourses,
  allCourses,
  loading,
  courseMessage,
  handleEnroll,
  handleDrop,
  handleLogout,
}) {
  const [activeTab, setActiveTab] = useState("my-courses");

  function getCourseInformation(courseId) {
    return allCourses.find(function (course) {
      return course.id === courseId;
    });
  }

  function isStudentEnrolled(courseId) {
    return myCourses.some(function (course) {
      return course.course_id === courseId;
    });
  }

  return (
    <div className="student-page">
      <div className="dashboard-card">
        <Header
          name={user.username}
          handleLogout={handleLogout}
        />

        <div className="dashboard-tabs">
          <button
            className={
              activeTab === "my-courses"
                ? "tab-button active-tab"
                : "tab-button"
            }
            onClick={function () {
              setActiveTab("my-courses");
            }}
          >
            Your Courses
          </button>

          <button
            className={
              activeTab === "add-courses"
                ? "tab-button active-tab"
                : "tab-button"
            }
            onClick={function () {
              setActiveTab("add-courses");
            }}
          >
            Add Courses
          </button>
        </div>

        <main className="dashboard-content">
          {courseMessage !== "" && (
            <p className="course-message">
              {courseMessage}
            </p>
          )}

          {loading === true && (
            <p className="status-text">
              Loading courses...
            </p>
          )}

          {loading === false &&
            activeTab === "my-courses" && (
              <MyCoursesTable
                myCourses={myCourses}
                getCourseInformation={getCourseInformation}
                handleDrop={handleDrop}
              />
            )}

          {loading === false &&
            activeTab === "add-courses" && (
              <AddCoursesTable
                allCourses={allCourses}
                isStudentEnrolled={isStudentEnrolled}
                handleEnroll={handleEnroll}
              />
            )}
        </main>
      </div>
    </div>
  );
}

function MyCoursesTable({
  myCourses,
  getCourseInformation,
  handleDrop,
}) {
  if (myCourses.length === 0) {
    return (
      <p className="status-text">
        You are not enrolled in any courses.
      </p>
    );
  }

  return (
    <div className="table-container">
      <table className="course-table">
        <thead>
          <tr>
            <th>Course Name</th>
            <th>Teacher</th>
            <th>Time</th>
            <th>Students Enrolled</th>
            <th>Drop</th>
          </tr>
        </thead>

        <tbody>
          {myCourses.map(function (enrollment) {
            const course = getCourseInformation(
              enrollment.course_id
            );

            let teacher = "Not available yet";
            let time = "Not available yet";
            let enrolledAmount = "Not available yet";

            if (course) {
              teacher = course.teacher;

              if (course.time) {
                time = course.time;
              }

              enrolledAmount =
                course.enrolled + "/" + course.capacity;
            }

            return (
              <tr key={enrollment.course_id}>
                <td>{enrollment.course_name}</td>
                <td>{teacher}</td>
                <td>{time}</td>
                <td>{enrolledAmount}</td>

                <td>
                  <button
                    className="drop-button"
                    onClick={function () {
                      handleDrop(
                        enrollment.course_id
                      );
                    }}
                  >
                    Remove
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function AddCoursesTable({
  allCourses,
  isStudentEnrolled,
  handleEnroll,
}) {
  if (allCourses.length === 0) {
    return (
      <p className="status-text">
        No courses are available.
      </p>
    );
  }

  return (
    <div className="table-container">
      <table className="course-table">
        <thead>
          <tr>
            <th>Course Name</th>
            <th>Teacher</th>
            <th>Time</th>
            <th>Students Enrolled</th>
            <th>Add Course</th>
          </tr>
        </thead>

        <tbody>
          {allCourses.map(function (course) {
            const alreadyEnrolled =
              isStudentEnrolled(course.id);

            const courseIsFull =
              course.enrolled >= course.capacity;

            let action;

            if (alreadyEnrolled) {
              action = (
                <span className="enrolled-text">
                  Enrolled
                </span>
              );
            } else if (courseIsFull) {
              action = (
                <span className="full-text">
                  Full
                </span>
              );
            } else {
              action = (
                <button
                  className="add-button"
                  onClick={function () {
                    handleEnroll(course.id);
                  }}
                >
                  Add
                </button>
              );
            }

            return (
              <tr key={course.id}>
                <td>{course.name}</td>
                <td>{course.teacher}</td>

                <td>
                  {course.time
                    ? course.time
                    : "Not available"}
                </td>

                <td>
                  {course.enrolled}/{course.capacity}
                </td>

                <td>{action}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default StudentDashboard;