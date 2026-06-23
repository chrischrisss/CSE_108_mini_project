import { useState } from "react";
import Header from "../components/Header";

function TeacherDashboard({
  user,
  teacherClasses,
  selectedTeacherClass,
  teacherRoster,
  teacherLoading,
  teacherMessage,
  loadTeacherRoster,
  handleUpdateGrade,
  handleLogout,
}) {
  const [activeView, setActiveView] = useState("classes");
  const [gradeChanges, setGradeChanges] = useState({});
  const [savingGrades, setSavingGrades] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  function openRoster(course) {
    setGradeChanges({});
    setSaveMessage("");
    setActiveView("roster");
    loadTeacherRoster(course);
  }

  function showClasses() {
    setGradeChanges({});
    setSaveMessage("");
    setActiveView("classes");
  }

  function changeGrade(enrollmentId, grade) {
    setGradeChanges(function (currentGrades) {
      return {
        ...currentGrades,
        [enrollmentId]: grade,
      };
    });

    setSaveMessage("");
  }

  async function saveGrades() {
    const changedGrades = Object.entries(gradeChanges);

    if (changedGrades.length === 0) {
      return;
    }

    setSavingGrades(true);
    setSaveMessage("");

    for (const [enrollmentId, grade] of changedGrades) {
      await handleUpdateGrade(Number(enrollmentId), grade);
    }

    setGradeChanges({});
    setSavingGrades(false);
    setSaveMessage("Grades updated.");
  }

  const message = saveMessage || teacherMessage;

  return (
    <div className="student-page">
      <div className="dashboard-card">
        <Header
          name={user.username}
          handleLogout={handleLogout}
        />

        <div className="dashboard-tabs">
          {activeView === "classes" ? (
            <button className="tab-button active-tab">
              Your Courses
            </button>
          ) : (
            <>
              <button
                className="tab-button"
                onClick={showClasses}
              >
                Back to Courses
              </button>

              <button className="tab-button active-tab">
                {selectedTeacherClass
                  ? selectedTeacherClass.name
                  : "Class Roster"}
              </button>
            </>
          )}
        </div>

        <main className="dashboard-content">
          {message !== "" && (
            <p className="course-message">
              {message}
            </p>
          )}

          {teacherLoading === true && (
            <p className="status-text">
              Loading classes...
            </p>
          )}

          {teacherLoading === false &&
            activeView === "classes" && (
              <TeacherCoursesTable
                teacherClasses={teacherClasses}
                openRoster={openRoster}
              />
            )}

          {teacherLoading === false &&
            activeView === "roster" && (
              <TeacherRosterTable
                teacherRoster={teacherRoster}
                gradeChanges={gradeChanges}
                changeGrade={changeGrade}
                saveGrades={saveGrades}
                savingGrades={savingGrades}
              />
            )}
        </main>
      </div>
    </div>
  );
}

function TeacherCoursesTable({
  teacherClasses,
  openRoster,
}) {
  if (teacherClasses.length === 0) {
    return (
      <p className="status-text">
        You do not have any classes.
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
            <th>Capacity</th>
            <th>Roster</th>
          </tr>
        </thead>

        <tbody>
          {teacherClasses.map(function (course) {
            return (
              <tr key={course.id}>
                <td>{course.name}</td>
                <td>{course.teacher}</td>
                <td>
                  {course.time
                    ? course.time
                    : "Not available"}
                </td>
                <td>{course.enrolled}/{course.capacity}</td>
                <td>
                  <button
                    className="add-button"
                    onClick={function () {
                      openRoster(course);
                    }}
                  >
                    View
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

function TeacherRosterTable({
  teacherRoster,
  gradeChanges,
  changeGrade,
  saveGrades,
  savingGrades,
}) {
  if (teacherRoster.length === 0) {
    return (
      <p className="status-text">
        No students are enrolled in this class.
      </p>
    );
  }

  const hasChanges = Object.keys(gradeChanges).length > 0;

  return (
    <>
      <div className="table-container">
        <table className="course-table">
          <thead>
            <tr>
              <th>Student Name</th>
              <th>Grade</th>
            </tr>
          </thead>

          <tbody>
            {teacherRoster.map(function (enrollment) {
              return (
                <tr key={enrollment.enrollment_id}>
                  <td>{enrollment.username}</td>
                  <td>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      value={
                        gradeChanges[enrollment.enrollment_id] ??
                        enrollment.grade ??
                        ""
                      }
                      onChange={function (event) {
                        changeGrade(
                          enrollment.enrollment_id,
                          event.target.value
                        );
                      }}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <button
        className="login-button"
        disabled={!hasChanges || savingGrades}
        onClick={saveGrades}
      >
        {savingGrades ? "Saving..." : "Save Grade Changes"}
      </button>
    </>
  );
}

export default TeacherDashboard;
