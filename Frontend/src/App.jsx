import { useState } from "react";
import Login from "./pages/Login";
import StudentDashboard from "./pages/StudentDashboard";
import TeacherDashboard from "./pages/TeacherDashboard"
import AdminDashboard from "./pages/AdminDashboard";

// import TeacherDashboard from "./pages/TeacherDashboard"; Add this back for teacher section Uday

import "./App.css";

function App() {
  const [user, setUser] = useState(null);

  const [myCourses, setMyCourses] = useState([]);
  const [allCourses, setAllCourses] = useState([]);

  const [loading, setLoading] = useState(false);
  const [courseMessage, setCourseMessage] = useState("");

  //Teacher Part
  const [teacherClasses, setTeacherClasses] = useState([]);
  const [selectedTeacherClass, setSelectedTeacherClass] = useState(null);
  const [teacherRoster, setTeacherRoster] = useState([]);
  
  const [teacherLoading, setTeacherLoading] = useState(false);
  const [teacherMessage, setTeacherMessage] = useState("");

  const [adminData, setAdminData] = useState({
    users: [],
    courses: [],
    enrollments: [],
  });
  const [adminLoading, setAdminLoading] = useState(false);
  const [adminMessage, setAdminMessage] = useState("");

  async function handleLogin(username, password, setMessage) {
  if (username.trim() === "" || password.trim() === "") {
    setMessage("Please enter both username and password.");
    return;
  }

  setMessage("Logging in...");

  try {
    const response = await fetch("/login", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      credentials: "include",

      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      setMessage(data.msg || "Login failed.");
      return;
    }

    const userResponse = await fetch("/me", {
      method: "GET",
      credentials: "include",
    });

    const userData = await userResponse.json();
    console.log("User information:", userData);

    if (!userResponse.ok) {
      setMessage(
        "Login worked, but user information could not be loaded."
      );
      return;
    }

    if (userData.role === "teacher") {
      setUser(userData);
      setMessage("");

      await loadTeacherData();

      return;
    }

    if (userData.role === "admin") {
      setUser(userData);
      setMessage("");

      await loadAdminData();

      return;
    }

    if (userData.role !== "student") {
      setMessage("Unknown account type.");
      return;
    }

    setUser(userData);
    setMessage("");

    await loadStudentData();
  } catch (error) {
    console.error("Login error:", error);
    setMessage("Could not connect to the backend.");
  }
}

  async function loadStudentData() {
    setLoading(true);
    setCourseMessage("");

    try {
      const myCoursesResponse = await fetch("/my-courses", {
        method: "GET",
        credentials: "include",
      });

      const allCoursesResponse = await fetch("/courses", {
        method: "GET",
        credentials: "include",
      });

      const myCoursesData = await myCoursesResponse.json();
      const allCoursesData = await allCoursesResponse.json();

      if (!myCoursesResponse.ok) {
        setCourseMessage(
          myCoursesData.error || "Could not load your courses."
        );
        return;
      }

      if (!allCoursesResponse.ok) {
        setCourseMessage(
          allCoursesData.error || "Could not load available courses."
        );
        return;
      }

      setMyCourses(myCoursesData);
      setAllCourses(allCoursesData);
    } catch (error) {
      console.error("Course loading error:", error);
      setCourseMessage("Could not connect to the backend.");
    } finally {
      setLoading(false);
    }
  }

  async function loadTeacherData() {
    setTeacherLoading(true);
    setTeacherMessage("");

    try {
      const response = await fetch("/teacher/classes", {
        method: "GET",
        credentials: "include",
      });

      const data = await response.json();

      if (!response.ok) {
        setTeacherMessage(data.error || "Could not load teacher classes.");
        return;
      }

      setTeacherClasses(data);
    } catch (error) {
      console.error("Teacher classes error:", error);
      setTeacherMessage("Could not connect to the backend.");
    } finally {
      setTeacherLoading(false);
    }
  }

  async function loadTeacherRoster(course) {
    setSelectedTeacherClass(course);
    setTeacherRoster([]);
    setTeacherMessage("");

    try {
      const response = await fetch(`/teacher/class/${course.id}`, {
        method: "GET",
        credentials: "include",
      });

      const data = await response.json();

      if (!response.ok) {
        setTeacherMessage(data.error || "Could not load class roster.");
        return;
      }

      setTeacherRoster(data);
    } catch (error) {
      console.error("Teacher roster error:", error);
      setTeacherMessage("Could not connect to the backend.");
    }
  }

  async function loadAdminData() {
    setAdminLoading(true);
    setAdminMessage("");

    try {
      const response = await fetch("/admin/data", {
        method: "GET",
        credentials: "include",
      });

      const data = await response.json();

      if (!response.ok) {
        setAdminMessage(data.error || "Could not load admin data.");
        return;
      }

      setAdminData(data);
    } catch (error) {
      console.error("Admin data error:", error);
      setAdminMessage("Could not connect to the backend.");
    } finally {
      setAdminLoading(false);
    }
  }

  async function adminAction(url, method, body) {
    setAdminMessage("");

    try {
      const options = {
        method: method,
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      };

      if (body !== undefined) {
        options.body = JSON.stringify(body);
      }

      const response = await fetch(url, options);
      const data = await response.json();

      if (!response.ok) {
        setAdminMessage(data.error || "Admin action failed.");
        return;
      }

      await loadAdminData();
      setAdminMessage(data.message || "Admin action completed.");
    } catch (error) {
      console.error("Admin action error:", error);
      setAdminMessage("Could not connect to the backend.");
    }
  }

    async function handleUpdateGrade(enrollmentId, grade) {
    setTeacherMessage("");

    try {
      const response = await fetch("/teacher/grade", {
        method: "PUT",

        headers: {
          "Content-Type": "application/json",
        },

        credentials: "include",

        body: JSON.stringify({
          enrollment_id: enrollmentId,
          grade: grade,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setTeacherMessage(data.error || "Could not update grade.");
        return;
      }

      setTeacherMessage(data.message || "Grade updated.");

      if (selectedTeacherClass !== null) {
        await loadTeacherRoster(selectedTeacherClass);
      }
    } catch (error) {
      console.error("Grade update error:", error);
      setTeacherMessage("Could not connect to the backend.");
    }
  }

  async function handleEnroll(courseId) {
    setCourseMessage("");

    try {
      const response = await fetch("/enroll", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        credentials: "include",

        body: JSON.stringify({
          course_id: courseId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setCourseMessage(data.error || "Could not enroll in course.");
        return;
      }

      setCourseMessage(data.message || "Enrolled successfully.");

      await loadStudentData();
    } catch (error) {
      console.error("Enrollment error:", error);
      setCourseMessage("Could not connect to the backend.");
    }
  }

  async function handleDrop(courseId) {
    setCourseMessage("");

    try {
      const response = await fetch("/drop", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        credentials: "include",

        body: JSON.stringify({
          course_id: courseId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setCourseMessage(data.error || "Could not drop course.");
        return;
      }

      setCourseMessage(data.message || "Course dropped.");

      await loadStudentData();
    } catch (error) {
      console.error("Drop course error:", error);
      setCourseMessage("Could not connect to the backend.");
    }
  }

  async function handleLogout() {
    try {
      await fetch("/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout error:", error);
    }

    setUser(null);
    setMyCourses([]);
    setAllCourses([]);
    setCourseMessage("");

    setTeacherClasses([]);
    setSelectedTeacherClass(null);
    setTeacherRoster([]);
    setTeacherMessage("");

    setAdminData({ users: [], courses: [], enrollments: [] });
    setAdminMessage("");

  }

  if (user === null) {
    return <Login handleLogin={handleLogin} />;
  }

  if (user.role === "student") {
    return (
      <StudentDashboard
        user={user}
        myCourses={myCourses}
        allCourses={allCourses}
        loading={loading}
        courseMessage={courseMessage}
        handleEnroll={handleEnroll}
        handleDrop={handleDrop}
        handleLogout={handleLogout}
      />
    );
  }

  if (user.role === "teacher") {
    return (
      <TeacherDashboard
        user={user}
        teacherClasses={teacherClasses}
        selectedTeacherClass={selectedTeacherClass}
        teacherRoster={teacherRoster}
        teacherLoading={teacherLoading}
        teacherMessage={teacherMessage}
        loadTeacherRoster={loadTeacherRoster}
        handleUpdateGrade={handleUpdateGrade}
        handleLogout={handleLogout}
      />
    );
  }

  if (user.role === "admin") {
    return (
      <AdminDashboard
        user={user}
        adminData={adminData}
        adminLoading={adminLoading}
        adminMessage={adminMessage}
        adminAction={adminAction}
        handleLogout={handleLogout}
      />
    );
  }

  return (
    <div className="page">
      <p>Unknown account type.</p>

      <button onClick={handleLogout}>
        Sign Out
      </button>
    </div>
  );
}

export default App;
