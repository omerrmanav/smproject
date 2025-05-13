# Resit Exam Management System

## 🚀 Overview

This project is a **Django-based system** designed to help manage courses, students, and exams, with a special focus on handling **resit (makeup) exams**. It aims to streamline the academic administration process for students, teachers, and faculty.

With this system:
* Teachers and faculty can manage course details, student enrollments, and grades.
* They can post important announcements, including specific details for resit exams.
* Students can view their grades, track their academic progress, and find information about any resit exams they might be eligible for.

## ✨ Features

The system boasts a range of features to support academic management:

* **👤 User Roles**: Clearly defined roles such as `Student`, `Teacher`, and `Faculty`, each with appropriate permissions and access levels.
* **📚 Course Management**:
    * Creation and administration of courses with details like `course_code`, `course_name`, and `credits`.
    * Assignment of teachers to courses.
    * Configuration of weighting for `midterm_weight` and `final_weight` exams.
* **🎓 Student Enrollment**: Easy enrollment of students into available courses.
* **📊 Grading System**:
    * Input fields for `midterm_grade` and `final_grade`.
    * Automatic calculation of final scores and corresponding letter grades (e.g., AA, BA, BB, ..., FF).
    * Logic to determine eligibility for resit exams based on grades (typically for `DC` or `FF`).
* **📢 Announcements**: A module for faculty to post general announcements to users.
* **📄 File Uploads**: Capability for faculty to upload and share relevant files (e.g., course syllabi, lecture notes).
* **🔁 Resit Exam Announcements**:
    * Dedicated section for announcing resit exams.
    * Details include the specific `Course`, `exam_datetime` (date and time), and `exam_place`.
    * Option for `additional_info` (rules, instructions) and `attached_file` (exam topics, seating plans).
* **💯 Resit Grades**:
    * Functionality to record `ResitGrade` for students who take a resit exam.
    * Automatic recalculation of the student's final score and letter grade incorporating the resit exam result.
* **🗓️ Course Sessions**:
    * Management of course schedules, including `day_of_week`, `start_time`, `end_time`, and `location` for each session.

## 🏗️ Project Structure (Models)

The backbone of the system is its data structure, defined by Django models. These models represent the different entities and their relationships within the application:

* **`Profile`**: Manages user accounts and their assigned roles (`student`, `teacher`, `faculty`).
* **`Course`**: Contains all information pertinent to a course, such as its unique code (`course_code`), name, credit value, assigned teacher, and the grading weights for midterm and final exams.
* **`Enrollment`**: Links a `student` to a `course`. This model is crucial as it stores individual student grades (`midterm_grade`, `final_grade`), tracks if a student `applied_for_makeup`, and includes methods to `calculate_final_score()` and `get_letter_grade()`. It also determines if a student `is_eligible_for_makeup()`.
* **`Announcement`**: Used by `faculty` to publish general announcements with a `title` and `content`.
* **`UploadedFile`**: Enables `faculty` to upload files, storing the `title`, `file` path, and `uploader` information.
* **`ResitExamAnnouncement`**: Provides detailed information about resit exams, linking to a `Course` and specifying the `exam_datetime`, `exam_place`, any `additional_info`, and an optional `attached_file`.
* **`CourseSession`**: Defines the schedule for course meetings, including `day_of_week`, `start_time`, `end_time`, and `location`.
* **`ResitGrade`**: A dedicated model to store a student's `grade` in a resit exam, linked to their original `Enrollment`. This model includes methods to `calculate_new_average_with_resit()` and `get_new_letter_grade_with_resit()`.

## 🛠️ How to Use (General Idea)

* **Faculty/Teachers**:
    1.  Log in to the system.
    2.  Add and manage courses.
    3.  Enroll students in their respective courses.
    4.  Input midterm and final grades.
    5.  Post general announcements or specific resit exam announcements.
    6.  Upload relevant course materials or exam-related files.
    7.  Enter resit grades after makeup exams.
* **Students**:
    1.  Log in to their accounts.
    2.  View their enrolled courses.
    3.  Check their midterm, final, and (if applicable) resit grades.
    4.  See calculated final scores and letter grades.
    5.  Access announcements and information regarding resit exams.

This system is designed to simplify and organize the often-complex process of managing academic records, especially when it comes to resit examinations, ensuring clarity and efficiency for all users.

![Main Login Page](https://github.com/user-attachments/assets/5fa04ddc-f843-4eaf-b59d-4f360981c50c)

![Student Login Page](https://github.com/user-attachments/assets/cc0faeed-1ad3-4133-a1c4-7cdeb3dbb184)

![Student Dashboard](https://github.com/user-attachments/assets/a4b9e136-8878-4ede-b7e9-8d8b999d2ecc)

![Student Course and Resit Information Page](https://github.com/user-attachments/assets/d8b23fa8-4bf3-40e1-8263-3113ca1f03c9)

![Student Announcement Page](https://github.com/user-attachments/assets/d6424c84-af04-46de-9253-09f1e4f5840a)

![Student Schedule](https://github.com/user-attachments/assets/64a1e480-70c6-49cf-8613-447543915a24)

![Instructor Login Page](https://github.com/user-attachments/assets/b403ca84-9c9f-4e0e-8a2c-0d3353e38465)

![Instructor Grading Page](https://github.com/user-attachments/assets/3595fc1c-577c-47e8-a91c-d83ec2a795e8)

![Instructor Resit Applications Page](https://github.com/user-attachments/assets/67e3ca22-1cbf-4713-85b8-371652eb4405)

![Instructor Enter Resit Grade Page](https://github.com/user-attachments/assets/bf46f0cc-1ae6-413a-9e8a-b5b5b61b9f9a)

![Instructor Schedule](https://github.com/user-attachments/assets/418a5229-7c62-49a9-a4d7-0abc7ee9672c)

![Faculty Login Page](https://github.com/user-attachments/assets/f8a36c6a-9f10-4cef-92d7-2e6ff9a3a4ac)

![Faculty Dashboard](https://github.com/user-attachments/assets/b17dd4fa-7a21-4d2c-b89f-cc93c1450000)

![Faculty Edit Announcement Page](https://github.com/user-attachments/assets/25e99ec5-6ae1-4e6c-88ca-b29ef9e605e7)


