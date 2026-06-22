Open two terminals from the project folder.

1. Start the Flask backend:

cd Backend
python app.py

2. Start the React frontend:

cd Frontend
npm install
npm run dev

Open the Vite address shown in the terminal, usually `http://localhost:5173`.

## Accounts

All accounts use this password:

"password"

(No "")

Admin account:

admin

Students:

- Ava Johnson
- Liam Smith
- Emma Williams
- Noah Brown
- Olivia Davis
- Ethan Miller
- Sophia Wilson
- Mason Moore
- Isabella Taylor
- James Anderson

Teachers and courses:

|           Teacher                 |               Courses                        |
|-----------------------------------|----------------------------------------------|
| Dr. Grace Lee                     | Introduction to Programming; Data Structures |
| Dr. Daniel Clark                  | Calculus I; Calculus II                      |
| Dr. Mia Rodriguez                 | General Biology; Genetics                    |
| Dr. Henry Walker                  | World History; United States History         |
| Dr. Chloe Harris                  | English Composition; Creative Writing        |

Each new course has a capacity of 30 students.

## Features

- Students can view classes, enroll, and drop a class.
- Teachers can view their classes, view enrolled students, and enter grades from 1 to 100.
- Admins can create, read, update, and delete users, courses, and enrollments.