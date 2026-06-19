import { useState } from "react";
import Login from "./pages/Login";
import StudentDashboard from "./pages/StudentDashboard";

// import TeacherDashboard from "./pages/TeacherDashboard"; Add this back for teacher section Uday

import "./App.css";

function App() {
  const [user, setUser] = useState(null);

  const [myCourses, setMyCourses] = useState([]);
  const [allCourses, setAllCourses] = useState([]);

  const [loading, setLoading] = useState(false);
  const [courseMessage, setCourseMessage] = useState("");

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
      setMessage(
        "Logged in, but make the Teacher Dashboard UDAY !!."
      );

      await fetch("/logout", {
        method: "POST",
        credentials: "include",
      });

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